"""Checks the report's prose against its evidence (build.sh runs it; ./build.sh final fails on what it reports).

Every sentence, list item, caption and table row of report_2.tex outside a \\placeholder is a claim. claims.json
gives each claim its evidence, which the verifier (see .claude/skills/verify-report) finds and this script
re-checks on every build, so that a claim whose evidence changes or disappears shows up again:
- {"path": "<repository path>", "quote": "<text>"}: the quote is in that file
- {"cite": "<bib key>", "quote": "<text>"}: the quote is in the reference's text (sources/<key>.txt)
- {"issue": <number>, "state": "OPEN" | "CLOSED"}: the GitHub issue is still in that state
Quotes match ignoring case, spacing and punctuation. Every number of a claim (in digits; "three" is not checked)
must appear in one of its quotes, every reference it cites must be quoted, and every repository path it names in
\\texttt or a GitHub link must exist. "evidence": [] says the claim states nothing checkable, "evidence": null
that nobody has verified it; a claim whose text changes is a new claim.

Usage: python3 verify.py [--sync] [--allow-unverified]
  --sync              add an unverified entry for every new claim and drop the entries of claims no longer in
                      the report
  --allow-unverified  fail only on broken evidence, not on claims nobody has verified yet (CI, while prose is
                      being written; ./build.sh final allows neither)
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import urllib.request
from glob import glob
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEDGER = HERE / "claims.json"
SOURCES = HERE / "sources"  # the references' texts, made on demand (gitignored)
LOCAL = {"Paper": ROOT / "emf/hybrid-quantum-annealing-for-large-scale-exam-scheduling.pdf",
         "Notebook": ROOT / "emf/QuantumExamScheduling.ipynb"}  # the other keys come from arXiv

NUMBER = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?!\w)")
CITE = re.compile(r"\\cites?(?:\s*(?:\[[^\]]*\])*\{[^}]*\})+")  # \cites[loc]{A}[loc]{B} too
NOT_NUMBERS = re.compile(rf"{CITE.pattern}|\\(?:[cC]?ref|label|texttt|href|url)(?:\[[^\]]*\])*(?:\{{[^}}]*\}})+|\\#\d+")
REPO_LINK = re.compile(r"https://github\.com/Alef-Keuffer/qmde/blob/[^/]+/([^}\s]+)")


def args_end(text, i, n):
    """The index after the n brace groups that start at i (optional [..] groups skipped)."""
    for _ in range(n):
        while text[i].isspace() or text[i] in "*[":
            i = text.index("]", i) + 1 if text[i] == "[" else i + 1
        depth, i = 1, i + 1
        while depth:
            depth += {"{": 1, "}": -1}.get(text[i], 0) * (text[i - 1] != "\\")
            i += 1
    return i


def drop(text, command, n, keep_last=False, around=""):
    """text without each \\command and its n arguments, or with only its last one (between around) when
    keep_last."""
    while (m := re.search(rf"\\{command}\b", text)):
        end = args_end(text, m.end(), n)
        inner = text[args_end(text, m.end(), n - 1):end].strip()[1:-1] if keep_last else ""
        text = text[:m.start()] + (around + inner + around if keep_last else "") + text[end:]
    return text


def claims(tex):
    """Each sentence, list item, caption and table row of the document's body, whitespace collapsed."""
    body = tex.split(r"\begin{document}")[1].split(r"\end{document}")[0]
    body = re.sub(r"(?<!\\)%.*", "", body)
    body = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", "", body, flags=re.S)
    body = drop(body, "placeholder", 3)
    for command in ("section", "subsection", "paragraph", "label"):
        body = drop(body, command, 1)
    body = drop(body, "caption", 1, keep_last=True)
    for note in ("sidenote", "footnote"):  # a claim of its own
        body = drop(body, note, 1, keep_last=True, around="\n\n")
    body = re.sub(r"^\s*\\(?:begin|end|input|VerbatimInput|[a-z]*rule|footnotesize|small|maketitle|tableofcontents"
                  r"|appendix|printbibliography)\b.*$", "", body, flags=re.M)
    body = re.sub(r"([.!?])\s*\\\]", r"\1\\]", body)  # a sentence ending in display maths ends after it
    units = re.split(r"\n\s*\n|\\item\b|\\\\|(?:(?<=[.!?])|(?<=[.!?]\\\]))\s+(?=[A-Za-z])", body)
    units = [" ".join(u.split()) for u in units]
    return [u for u in units if re.search(r"[A-Za-z]{2}", u)]


def plain(text):
    """text for quote matching: lower case, letters and digits only."""
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKC", text).lower())


def numbers(text):
    return {float(n) for n in NUMBER.findall(NOT_NUMBERS.sub(" ", text))}  # so 1 is 1.0


def cited(text):
    """The bib keys text cites."""
    return {k.strip() for c in CITE.findall(text) for g in re.findall(r"\{([^}]*)\}", c) for k in g.split(",")}


def source(key):
    """The text of reference key, made into sources/<key>.txt on first use; None when it cannot be."""
    cached = SOURCES / f"{key}.txt"
    if not cached.exists() or key in LOCAL and LOCAL[key].stat().st_mtime > cached.stat().st_mtime:
        if key == "Notebook":
            cells = json.loads(LOCAL[key].read_text(encoding="utf-8"))["cells"]
            text = "\n".join(f"[cell {c.get('execution_count')}]\n{''.join(c['source'])}" for c in cells)
        elif not shutil.which("pdftotext"):
            return None
        else:
            pdf = LOCAL.get(key)
            if pdf is None:
                bib = (HERE / "references.bib").read_text(encoding="utf-8")
                entry = re.search(rf"@\w+\{{{key},(.*?)\n\}}", bib, re.S)
                eprint = entry and re.search(r"eprint\s*=\s*\{([^}]*)\}", entry[1])
                if not eprint:
                    return None
                pdf = SOURCES / f"{key}.pdf"
                SOURCES.mkdir(exist_ok=True)
                try:
                    urllib.request.urlretrieve(f"https://arxiv.org/pdf/{eprint[1]}", pdf)
                except OSError:
                    return None
            try:
                text = subprocess.run(["pdftotext", pdf, "-"], capture_output=True, check=True, text=True).stdout
            except (OSError, subprocess.CalledProcessError):
                return None
        SOURCES.mkdir(exist_ok=True)
        cached.write_text(text, encoding="utf-8")
    return cached.read_text(encoding="utf-8")


def issue_state(number):
    try:
        return subprocess.run(["gh", "issue", "view", str(number), "--json", "state", "--jq", ".state"], cwd=ROOT,
                              capture_output=True, check=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def check_evidence(item):
    """(problem, warning) of one piece of evidence; each None when there is none."""
    if "issue" in item:
        state = issue_state(item["issue"])
        if state is None:
            return None, f"issue #{item['issue']} unchecked: gh failed"
        return (None if state == item["state"] else f"issue #{item['issue']} is {state}, not {item['state']}"), None
    if "path" in item:
        path = ROOT / item["path"]
        if not path.is_file():
            return f"{item['path']} does not exist", None
        text, where = path.read_text(encoding="utf-8"), item["path"]
    else:
        text, where = source(item["cite"]), f"[{item['cite']}]"
        if text is None:
            return None, f"{where} unchecked: no text of it (sources/{item['cite']}.txt)"
    return (None if plain(item["quote"]) in plain(text) else f"quote not in {where}: {item['quote'][:80]!r}"), None


def missing_paths(claim):
    """The repository paths that claim names and that neither exist nor are ignored build outputs."""
    paths = [p.replace(r"\_", "_") for p in re.findall(r"\\texttt\{([^{}\s]*/[^{}\s]*)\}", claim)]
    paths += REPO_LINK.findall(claim)
    missing = []
    for p in paths:
        pattern = re.sub(r"<[^>]*>", "*", p)
        if glob(str(ROOT / pattern)) or glob(str(ROOT / pattern) + "*"):
            continue
        if subprocess.run(["git", "check-ignore", "-q", pattern.replace("*", "x")], cwd=ROOT,
                          capture_output=True).returncode:
            missing.append(p)
    return missing


def problems(claim, evidence):
    """(problems, warnings) of one claim of the report with its ledger evidence."""
    found = [f"names {p}, which does not exist" for p in missing_paths(claim)]
    if evidence is None:
        return found + ["unverified"], []
    warnings = []
    for item in evidence:
        problem, warning = check_evidence(item)
        found += [problem] if problem else []
        warnings += [warning] if warning else []
    quoted = set().union(*(numbers(item.get("quote", "")) for item in evidence))
    if evidence and (unsupported := sorted(numbers(claim) - quoted)):
        found.append(f"number(s) {', '.join(f'{n:g}' for n in unsupported)} in none of its quotes")
    for key in sorted(cited(claim) - {item.get("cite") for item in evidence}) if evidence else []:
        if source(key) is None:
            warnings.append(f"[{key}] unchecked: no text of it (sources/{key}.txt)")
        else:
            found.append(f"cites [{key}] but quotes nothing from it")
    return found, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sync", action="store_true", help="add new claims to claims.json, drop gone ones")
    parser.add_argument("--allow-unverified", action="store_true", help="fail only on broken evidence")
    args = parser.parse_args()
    report = claims((HERE / "report_2.tex").read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else []
    evidence = {e["claim"]: e for e in ledger}
    if args.sync:
        ledger = [evidence.get(c, {"claim": c, "evidence": None}) for c in dict.fromkeys(report)]
        LEDGER.write_text(json.dumps(ledger, indent="\t", ensure_ascii=False) + "\n", encoding="utf-8")
        evidence = {e["claim"]: e for e in ledger}
    failed = unverified = 0
    for claim in dict.fromkeys(report):
        found, warnings = problems(claim, evidence.get(claim, {}).get("evidence"))
        failed += bool(found)
        unverified += found == ["unverified"]
        if found or warnings:
            print("\n".join([claim[:120], *(f"  ✗ {p}" for p in found), *(f"  ? {w}" for w in warnings)]),
                  file=sys.stderr)
    gone = [e["claim"] for e in ledger if e["claim"] not in report]
    print(f"verify: {len(set(report))} claims, {failed} with problems ({unverified} only unverified), {len(gone)} "
          f"ledger entries for claims no longer in the report{' (--sync drops them)' if gone else ''}",
          file=sys.stderr)
    sys.exit(1 if failed - (unverified if args.allow_unverified else 0) else 0)


if __name__ == "__main__":
    main()
