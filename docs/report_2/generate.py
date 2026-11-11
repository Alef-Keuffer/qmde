"""Generates the parts of the Part II report that come from the code and from CI (build.sh runs it).

- generated/traceability.tex: Appendix A, one row per comment of the EMF chain that cites [Key locator]
- generated/metamodel-<name>.tex: Appendix C, a class diagram of each EMF .ecore
- generated/glossary.tex: the Glossary appendix, from emf/GLOSSARY.md
- generated/glossary-terms.tex: what \\term looks up: each glossary term and its plural, in lower case
- with --results: generated/validation-emf.tex (Section 4) and generated/results-emf.tex (Appendix B),
  and, when the results come from CI (--run-url), emf/CONTEXT.md's results table
"""
import argparse
import ast
import io
import json
import math
import re
import sys
import tokenize
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
EMF = HERE.parents[1] / "emf"
MODELS = EMF / "bundles/pt.up.feup.examschedule.model/model"
XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"
ECORE = "http://www.eclipse.org/emf/2002/Ecore"  # the annotation listing a class's OCL invariants
TEX = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{",
       "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}

CHAIN = EMF / "bundles/pt.up.feup.examschedule.chain"
SOURCES = [  # what Appendix A reads: (artefact, file, what it does)
    ("ATL", CHAIN / "transforms/problem2conflictgraph.atl", r"Problem $\to$ Conflict Graph"),
    ("Acceleo", CHAIN / "src/pt/up/feup/examschedule/chain/codegen/main.mtl",
     r"Conflict Graph and Solver Configuration $\to$ \texttt{solve\_<name>.py}"),
    ("Python", EMF / "python/examschedule.py", "the runtime the generated scripts call"),
]

KEYS = ("Paper", "Notebook", "Farhi", "Lucas", "Glover")  # bib keys = the code's citation tags
TAG = re.compile(r"\[(%s)(?: ([^\]]*))?\]" % "|".join(KEYS))  # [Key locator]
ATL_UNIT = re.compile(r"^((?:(?:unique|lazy|abstract|refining|nodefault|entrypoint|endpoint) )*rule) (\w+)"
                      r"|^helper\b.*\bdef\s*:\s*(\w+)")


def comment_blocks(lines, marker):
    """(first, last, text) of each run of consecutive lines that are only a comment."""
    blocks, start = [], None
    for i, line in enumerate([*lines, ""]):
        if line.strip().startswith(marker):
            start = i if start is None else start
        elif start is not None:
            text = " ".join(l.strip()[len(marker):].strip() for l in lines[start:i])
            blocks.append((start, i - 1, text))
            start = None
    return blocks


def atl_unit(lines, first, last):
    """An indented comment belongs to the enclosing rule, one at column 0 to the next rule or helper, and one
    with neither to the module."""
    candidates = reversed(lines[:first]) if lines[first][0].isspace() else lines[last + 1:]
    for line in candidates:
        if m := ATL_UNIT.match(line):
            return f"{m[1]} {m[2]}" if m[1] else f"helper {m[3]}"
    return "module"


def template_unit(lines, last):
    """The names the template assigns, at the comment's indentation, before the next blank line."""
    indent = len(lines[last]) - len(lines[last].lstrip())
    names = []
    for line in lines[last + 1:]:
        if not line.strip():
            break
        if (m := re.match(r"(\s*)(\w+)\s*=(?!=)", line)) and len(m[1]) == indent:
            names.append(m[2])
    return ", ".join(names)


def python_blocks(text):
    """(unit, text) of every docstring and comment block, a trailing comment being a block of its own;
    the unit is the innermost function or class around it."""
    tree = ast.parse(text)
    defs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]

    def unit(line):
        inner = max((d for d in defs if d.lineno <= line <= d.end_lineno), key=lambda d: d.lineno, default=None)
        return inner.name if inner else "module"

    blocks = [(d.lineno, d.name, " ".join(ast.get_docstring(d).split())) for d in defs if ast.get_docstring(d)]
    if doc := ast.get_docstring(tree):
        blocks.append((0, "module", " ".join(doc.split())))
    runs = []  # [first line, last line, own line?, comments]
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type != tokenize.COMMENT:
            continue
        line, own = token.start[0], token.line.lstrip().startswith("#")
        if own and runs and runs[-1][2] and runs[-1][1] == line - 1:
            runs[-1][1] = line
            runs[-1][3].append(token.string)
        else:
            runs.append([line, line, own, [token.string]])
    blocks += [(first, unit(first), " ".join(c.lstrip("#").strip() for c in comments))
               for first, _, _, comments in runs]
    return [(unit, text) for _, unit, text in sorted(blocks)]


def citations(path):
    """(unit, comment) for every comment block of the file citing a reference as [Key locator]."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".py":
        blocks = python_blocks(text)
    elif path.suffix == ".mtl":
        lines = text.replace("['['/]", "[").splitlines()  # Acceleo's escape for a literal bracket
        blocks = [(template_unit(lines, last), text) for _, last, text in comment_blocks(lines, "#")]
    else:
        lines = text.splitlines()
        blocks = [(atl_unit(lines, first, last), text) for first, last, text in comment_blocks(lines, "--")]
    return [(unit, text) for unit, text in blocks if TAG.search(text)]


def base(name):
    """The problem a run solves: a twin instance is named <name>_<method>."""
    return re.sub(r"_(qaoa|annealing)$", "", name)


def load_runs(results, instances):
    """Every results_<name>.json under results, each instance (in file order) before its twin."""
    order = [base(re.search(r"^problem (\w+)", p.read_text(encoding="utf-8"), re.M)[1])
             for p in sorted(instances.glob("*.exam"))]
    runs = [json.loads(p.read_text(encoding="utf-8")) for p in results.rglob("results_*.json")]
    if not runs:
        sys.exit(f"no results_*.json under {results}")
    if unknown := [r["instance"] for r in runs if base(r["instance"]) not in order]:
        sys.exit(f"results for instances not in {instances}: {', '.join(unknown)}")
    return sorted(runs, key=lambda r: (order.index(base(r["instance"])), r["instance"] != base(r["instance"])))


def method(run):
    s = run["solver"]
    if s["method"] == "ANNEALING":
        text = f"annealing, {s['reads']} reads × {s['sweeps']} sweeps"
    else:
        optimizer = {"NELDER_MEAD": "Nelder-Mead", "POWELL": "Powell"}.get(s["optimizer"], s["optimizer"])
        text = f"QAOA, depth {s['depth']}, {optimizer}, {s['max_iterations']} iterations, {s['shots']} shots"
    return text if s["penalty"] is None else f"{text}, penalty {s['penalty']:g}"


def prob(p):
    """Three decimals, or two significant digits below 0.01 (0.0078, 0.00005); a dash when skipped."""
    if p is None:
        return "–"
    if p >= 0.01 or p == 0:
        return f"{p:.3f}"
    return f"{p:.{1 - math.floor(math.log10(p))}f}".rstrip("0")


def outcome(run):
    s = run["schedule"]
    return f"{s['cost']:g}, {', '.join(s['unscheduled']) or 'none'}"


def optimum(run):
    return "skipped" if run["optimal_cost"] is None else f"{run['optimal_cost']:g}"


def context_results(runs, run_url):
    """CONTEXT.md's results table, from a CI run's results."""
    claim = "; every schedule found is feasible and optimal" if all(r["optimal"] for r in runs) else ""
    rows = [f"| {base(r['instance'])} | {r['variables']} | {method(r)} | {outcome(r)} | {optimum(r)} "
            f"| {prob(r['p_optimal'])} | {prob(r['p_feasible'])} |" for r in runs]
    return "\n".join([
        f"Results with the committed instances and seeds, from CI's `./build.sh` (Linux, the pinned "
        f"`requirements.txt`), [run {run_url.rsplit('/', 1)[1]}]({run_url}), written here by "
        f"`docs/report_2/build.sh`{claim}:",
        "",
        "| Instance | Variables | Method | Result (cost, unscheduled exams) | Optimal cost (baseline) "
        "| P(optimal) | P(feasible) |",
        "|---|---|---|---|---|---|---|",
        *rows])


def tex(text):
    return "".join(TEX.get(c, c) for c in text)


def type_name(feature):
    return feature.get("eType").rsplit("//", 1)[1]  # "ecore:EDataType …Ecore#//EString" or "#//Student"


def multiplicity(feature):
    lower, upper = feature.get("lowerBound", "0"), feature.get("upperBound", "1").replace("-1", "*")
    return lower if lower == upper else f"{lower}..{upper}"


def box(title, *compartments):
    """A UML box: the centred title lines, then each compartment below a rule."""
    lines = r"\\".join(rf"\multicolumn{{1}}{{c}}{{{line}}}" for line in title)
    lines += "".join(r"\\\hline " + (r"\\".join(c) or r"\strut") for c in compartments)
    return rf"\begin{{tabular}}{{l}}{lines}\end{{tabular}}"


def class_diagram(path):
    """A TikZ class diagram of an .ecore: classes with their attributes and OCL invariant names, enumerations,
    containments and references, laid out by graph drawing (styles in report_2.tex)."""
    # shortcut: no generalisations (no eSuperTypes in the metamodels yet); draw them when one appears.
    nodes, edges = [], []
    for c in ET.parse(path).getroot().findall("eClassifiers"):
        name = c.get("name")
        if c.get(XSI_TYPE) == "ecore:EEnum":
            literals = [tex(l.get("name")) for l in c.findall("eLiterals")]
            nodes.append(rf"\node[class] ({name}) {{{box(['«enumeration»', rf'\textbf{{{name}}}'], literals)}}};")
            continue
        attributes = []
        for f in c.findall("eStructuralFeatures"):
            m = multiplicity(f)
            if f.get(XSI_TYPE) == "ecore:EReference":
                style = "contain" if f.get("containment") == "true" else "reference"
                edges.append((name, type_name(f), style, tex(f"{f.get('name')} {m}")))
            else:
                default = f.get("defaultValueLiteral")
                attributes.append(tex(f"{f.get('name')}: {type_name(f)}" + ("" if m == "0..1" else f" [{m}]")
                                      + (f" = {default}" if default else "")))
        invariants = [rf"\textit{{inv}} {tex(n)}" for a in c.findall("eAnnotations") if a.get("source") == ECORE
                      for d in a.findall("details") if d.get("key") == "constraints" for n in d.get("value").split()]
        compartments = [attributes, invariants] if invariants else [attributes]
        nodes.append(rf"\node[class] ({name}) {{{box([rf'\textbf{{{name}}}'], *compartments)}}};")
    pairs, seen = Counter((s, t) for s, t, *_ in edges), Counter()
    for source, target, style, label in edges:
        # shortcut: two parallel edges at most (Conflict's first and second); fan out more when needed.
        bend = "" if pairs[source, target] == 1 else [", bend left=20", ", bend right=20, swap"][seen[source, target]]
        seen[source, target] += 1
        nodes.append(rf'\path ({source}) edge[{style}{bend}, "{label}" role] ({target});')
    return "\n".join([r"\begin{tikzpicture}[metamodel]", *nodes, r"\end{tikzpicture}"])


def splice(text, block):
    """text with what lies between the results markers replaced by block, between blank lines (a Markdown table
    would otherwise take the end marker for one of its rows)."""
    begin, end = "<!-- results:begin -->", "<!-- results:end -->"
    head, rest = text.split(begin)
    _, tail = rest.split(end)
    return f"{head}{begin}\n\n{block}\n\n{end}{tail}"


def cited(text):
    """text for TeX, each [Key locator] a \\cite."""
    out, pos = [], 0
    for m in TAG.finditer(text):
        locator = (m[2] or "").replace(")-(", ")--(")
        out += [tex(text[pos:m.start()]), rf"\cite[{tex(locator)}]{{{m[1]}}}" if locator else rf"\cite{{{m[1]}}}"]
        pos = m.end()
    return "".join(out) + tex(text[pos:])


def traceability():
    rows = []
    for artefact, path, does in SOURCES:
        rows += [r"\midrule", rf"\multicolumn{{2}}{{@{{}}l}}{{\textbf{{{artefact}}}, \texttt{{{tex(path.name)}}}: {does}}} \\"]
        rows += [rf"\texttt{{{tex(unit)}}} & {cited(text)} \\" for unit, text in citations(path)]
    return "\n".join([
        r"\begin{table}",
        r"\caption{Every ATL rule, template section and runtime step of the EMF chain that implements the "
        r"formulation or QAOA, with the reference its comment cites, read from the code.}\label{tab:traceability}",
        r"\small",
        r"\begin{tabularx}{\linewidth}{@{}l>{\raggedright\arraybackslash}X@{}}",
        r"\toprule",
        r"Unit & What it implements, as its comment says \\",
        *rows,
        r"\bottomrule",
        r"\end{tabularx}",
        r"\end{table}"])


def metamodel_figure(path):
    name = ET.parse(path).getroot().get("name")
    return "\n".join([
        r"\begin{figure}",
        class_diagram(path),
        rf"\caption{{The {name} metamodel, drawn from \texttt{{{path.name}}}.}}\label{{fig:metamodel-{path.stem}}}",
        r"\end{figure}"])


def source(run_url):
    """Where the numbers come from; a local run is a placeholder until CI's are in."""
    if run_url:
        return rf"\href{{{run_url}}}{{CI run {run_url.rsplit('/', 1)[1]}}}", ""
    return "a local run", (r"\placeholder{CI}{These EMF numbers come from a local run, not from CI}{Once CI has "
                           r"uploaded an \texttt{emf-results} artifact (push \#24 and \#25), rerun \texttt{build.sh}, "
                           r"or \texttt{build.sh --run <id>} for another branch's run.}")


def times_chance(run):
    if run is None or run["p_optimal"] is None:
        return "–"
    return rf"{prob(run['p_optimal'])} ({run['p_optimal'] / run['random_p_optimal']:.0f}$\times$)"


def validation_table(runs, run_url):
    """Section 4's table: P(optimal) of each Method on each instance, against chance."""
    origin, placeholder = source(run_url)
    by_problem = {}
    for r in runs:
        by_problem.setdefault(base(r["instance"]), {})[r["solver"]["method"]] = r
    rows = [rf"{tex(name)} & {next(iter(pair.values()))['variables']} "
            rf"& {prob(next(iter(pair.values()))['random_p_optimal'])} "
            rf"& {times_chance(pair.get('QAOA'))} & {times_chance(pair.get('ANNEALING'))} \\"
            for name, pair in by_problem.items()]
    return "\n".join([
        placeholder,
        r"\begin{table}",
        r"\caption{P(optimal) of the EMF chain on each test instance (\cref{app:instances}) by Method, against a "
        r"uniformly random bit string's; in brackets, how many times chance. Solver Configurations in \cref{tab:results-emf}; "
        rf"from {origin}.}}\label{{tab:validation-emf}}",
        r"\begin{tabular}{@{}lrrrr@{}}",
        r"\toprule",
        r"Instance & Variables & Random & QAOA & Simulated annealing \\",
        r"\midrule",
        *rows,
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}"])


def schedule(run):
    s = run["schedule"]
    batches = {}
    for exam, batch in s["assignments"]:
        batches.setdefault(batch, []).append(exam)
    text = "; ".join(f"{b}: {', '.join(exams)}" for b, exams in sorted(batches.items()))
    return tex(text if s["feasible"] else f"{text}; breaks {', '.join(s['broken'])}")


def results_tables(runs, run_url):
    """Appendix B's tables: every run's metrics, and the schedule each found."""
    origin, placeholder = source(run_url)
    metrics = [rf"{tex(base(r['instance']))} & {r['variables']} & {tex(method(r))} & {r['penalty']:g} "
               rf"& {tex(outcome(r))} & {optimum(r)} & {prob(r['p_optimal'])} & {prob(r['random_p_optimal'])} "
               rf"& {prob(r['p_feasible'])} & {prob(r['random_p_feasible'])} \\" for r in runs]
    schedules = [rf"{tex(base(r['instance']))} & {'QAOA' if r['solver']['method'] == 'QAOA' else 'annealing'} "
                 rf"& {schedule(r)} & {tex(', '.join(r['schedule']['unscheduled']) or 'none')} \\" for r in runs]
    return "\n".join([
        placeholder,
        r"\begin{table}",
        r"\caption{Every run of the EMF chain: each test instance solved by both Methods, with the committed "
        r"seeds; the Penalty Coefficient $A$ used, the Schedule's cost and Unscheduled Exams, the Baseline's "
        r"optimal cost, and P(optimal) and P(feasible) against a uniformly random bit string's. From "
        rf"{origin}.}}\label{{tab:results-emf}}",
        r"\footnotesize\setlength{\tabcolsep}{4pt}",
        r"\begin{tabularx}{\linewidth}{@{}lr>{\raggedright\arraybackslash}Xrlrrrrr@{}}",
        r"\toprule",
        r"& & & & & Optimal & \multicolumn{2}{c}{P(optimal)} & \multicolumn{2}{c@{}}{P(feasible)} \\",
        r"\cmidrule(lr){7-8}\cmidrule(l){9-10}",
        r"Instance & Var. & Method & $A$ & Result & cost & run & random & run & random \\",
        r"\midrule",
        *metrics,
        r"\bottomrule",
        r"\end{tabularx}",
        r"\end{table}",
        r"\begin{table}",
        rf"\caption{{The Schedule each run of \cref{{tab:results-emf}} found: the exams of each batch.}}"
        r"\label{tab:schedules-emf}",
        r"\footnotesize",
        r"\begin{tabularx}{\linewidth}{@{}ll>{\raggedright\arraybackslash}Xl@{}}",
        r"\toprule",
        r"Instance & Method & Batch: exams & Unscheduled \\",
        r"\midrule",
        *schedules,
        r"\bottomrule",
        r"\end{tabularx}",
        r"\end{table}"])


ENTRY = re.compile(r"\*\*([^*]+)\*\*(?: (\([^)]*\)))?:$")  # **Name**: or **Name** (qualifier):
CODE_BLOCK = re.compile(r"^(```|~~~|    )")
UNUSED = [  # Markdown GLOSSARY.md does not use, matched outside code spans: rendering it would go wrong silently
    ("a heading", re.compile(r"^\s*(#|[-=]{2,}\s*$)")), ("a list", re.compile(r"^\s*([-*+]|\d+[.)])\s")),
    ("a table", re.compile(r"^\s*\|")), ("a quote", re.compile(r"^\s*>")),
    ("a link", re.compile(r"\]\(|^\s*\[[^\]]*\]:")), ("HTML", re.compile(r"<[A-Za-z/!]|&#?\w+;")),
    ("emphasis", re.compile(r"[*_]"))]
TERM = re.compile(r"\*([^*\s][^*]*)\*")  # *Term*: a domain use of a glossary term, rendered as \term


def inline(text):
    """A glossary line's text for TeX: `code` monospace, "quotes" curly, *Term* through \\term."""
    parts = re.split(r"`([^`]*)`", text)
    return "".join(rf"\texttt{{{tex(p)}}}" if i % 2 else
                   TERM.sub(r"\\term{\1}", re.sub(r'"([^"]*)"', r"\\enquote{\1}", tex(p)))
                   for i, p in enumerate(parts))


def anchor(term):
    """The hypertarget of a glossary entry."""
    return "term:" + re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")


def plural(term):
    """A term's plural by the regular English rule, on its last word."""
    if re.search(r"(s|x|z|ch|sh)$", term, re.I):
        return term + "es"
    if re.search(r"[^aeiou]y$", term, re.I):
        return term[:-1] + "ies"
    return term + "s"


def glossary_terms(text):
    """What \\term looks up: each entry's name and its plural, in lower case, with the entry's anchor."""
    names = [name for _, entries in parse_glossary(text) for name, *_ in entries]
    table = {}
    for name in names:
        target = anchor(name)
        for form in (name, plural(name)):
            if table.setdefault(form.lower(), target) != target:
                sys.exit(f"GLOSSARY.md: {form} is both a term and a plural")
    return "\n".join(rf"\glossaryterm{{{form}}}{{{target}}}" for form, target in table.items())


def parse_glossary(text):
    """GLOSSARY.md's Language section as [group, [[name, qualifier, definition lines, avoid]]]; any Markdown the
    glossary does not use stops the build."""
    lines = text.splitlines()
    if "## Language" not in lines:
        sys.exit("GLOSSARY.md: no ## Language section")
    language = lines.index("## Language")
    groups = []  # [name, [[name, qualifier, definition lines, avoid]]]
    for n, line in enumerate(lines[language + 1:], language + 2):
        def reject(what):
            sys.exit(f"GLOSSARY.md line {n}: {what}: {line}")
        if not line.strip():
            continue
        if CODE_BLOCK.match(line):
            reject("a code block")
        group, entry = line.startswith("### "), ENTRY.match(line)
        avoid = line.startswith("_Avoid_: ")
        content = line[4:] if group else " ".join(filter(None, entry.groups())) if entry else \
            line[len("_Avoid_: "):] if avoid else line
        for what, pattern in UNUSED:
            if pattern.search(TERM.sub("", re.sub(r"`[^`]*`", "", content))):
                reject(what)
        if group:
            groups.append([content, []])
        elif entry:
            if not groups:
                reject("an entry outside a group")
            groups[-1][1].append([entry[1], entry[2], [], None])
        elif not groups or not groups[-1][1] or groups[-1][1][-1][3]:
            reject("text outside an entry")
        elif avoid and not groups[-1][1][-1][2]:
            reject("an Avoid line before the definition")
        elif avoid:
            groups[-1][1][-1][3] = content
        else:
            groups[-1][1][-1][2].append(content)
    return groups


def glossary(text):
    """The Glossary appendix from GLOSSARY.md's Language section: its groups in order, each a description list of
    its entries, each name the target of its \\term links, with their Avoid lines."""
    out = []
    for name, entries in parse_glossary(text):
        out += [rf"\subsection*{{{inline(name)}}}", r"\begin{description}"]
        for term, qualifier, definition, avoid in entries:
            label = rf"\hypertarget{{{anchor(term)}}}{{{inline(term)}}}" + \
                (rf" {{\normalfont{inline(qualifier)}}}" if qualifier else "")
            out.append(rf"\item[{label}] {inline(' '.join(definition))}" + (r"\par" if avoid else ""))
            if avoid:
                out.append(rf"{{\small\itshape Avoid: {inline(avoid)}}}")
        out.append(r"\end{description}")
    return "\n".join(out)


def write(name, text):
    (HERE / "generated" / name).write_text(f"% Generated by generate.py; do not edit.\n{text}\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--results", type=Path, help="a folder holding results_<name>.json files")
    parser.add_argument("--run-url", help="the CI run they come from; without it they count as a local run")
    args = parser.parse_args()
    (HERE / "generated").mkdir(exist_ok=True)
    write("traceability.tex", traceability())
    for ecore in MODELS.glob("*.ecore"):
        write(f"metamodel-{ecore.stem}.tex", metamodel_figure(ecore))
    text = (EMF / "GLOSSARY.md").read_text(encoding="utf-8")
    write("glossary.tex", glossary(text))
    write("glossary-terms.tex", glossary_terms(text))
    if args.results:
        runs = load_runs(args.results, EMF / "instances")
        write("validation-emf.tex", validation_table(runs, args.run_url))
        write("results-emf.tex", results_tables(runs, args.run_url))
        if args.run_url:
            context = EMF / "CONTEXT.md"
            context.write_text(splice(context.read_text(encoding="utf-8"), context_results(runs, args.run_url)),
                               encoding="utf-8")
        else:
            print("emf/CONTEXT.md left as it is: its results table comes from CI only", file=sys.stderr)


if __name__ == "__main__":
    main()
