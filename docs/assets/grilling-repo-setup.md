# Grilling session: is the repo set up correctly?

- **Date:** 2026-11-10.
- **Who:** Alef Keuffer, with Claude Code (Claude Opus 5.5) running the
  `grill-with-docs` skill (`grilling` + `domain-modeling`) from Matt Pocock's
  [Skills For Real Engineers](https://github.com/mattpocock/skills).
- **Result:** [#22](https://github.com/Alef-Keuffer/qmde/pull/22) (closes
  [#7](https://github.com/Alef-Keuffer/qmde/issues/7)); issues
  [#4](https://github.com/Alef-Keuffer/qmde/issues/4) and
  [#5](https://github.com/Alef-Keuffer/qmde/issues/5) closed; merged branches
  and worktrees removed.
- **Summary:** see "Reviewing the repository setup" in the
  [AI log](../llm_usage_2.md).

This is a structured record of the session, written from the Claude Code
session log. Alef's messages are quoted word for word. The AI's questions are
shortened to their decision and its recommended answer.

## 1. How it started

> /mattpocock-skills:grill-with-docs Is this repo set up correctly? What should we improve?

## 2. Facts the AI looked up

The skill has the AI look up facts itself and leave only decisions to the user.

- The local `main` was 61 commits behind `origin/main`, so the AI reviewed a
  copy of `origin/main` instead. The local `.project` edits and untracked
  `m2e.core.prefs` would block `git pull`, and the fast-forward would delete
  Alef's `tests/test2.py` (removed on `main` in `7f50798`).
- A teammate's commit `ca4c3cf` ("docs: llm usage…") also committed what a Java
  language server writes when it imports the bundles as Maven projects: the m2e
  nature and builder in five `.project` files, five `m2e.core.prefs` and
  `emf/bundles/pom.tycho`. Issue #7 was meant to prevent exactly that.
- #4 and #5 were done by PRs #12 and #13 but still open.
- No unit tests ran anywhere: neither `./build.sh` nor CI runs
  `python/test_examschedule.py` or `tools/test_*.py`.
- `emf/requirements.txt` had lower bounds only. Today's CI run on `main` gave
  different P(optimal)/P(feasible) than `emf/CONTEXT.md` (written the same day),
  with the same seeds (e.g. clique 0.98 against 0.94); the seeds do reach neal
  and Aer.
- The clone, `.venv`, `target/` and the worktrees live in Google Drive.
- The Glossary is titled "Exam-Slot Assignment" but lists "slot" under Batch's
  _Avoid_.
- Ten local branches and three worktrees held only work already on `main`
  (checked with `git cherry`); ten remote branches were Alef's, with merged or
  closed PRs.
- CI (`emf`, `emf-ide`) was green on `origin/main`, and the docs and ADRs agreed
  with the code.

## 3. Questions and answers

Each round, the AI asked every question it could ask without knowing the
answer to another open one, each with a recommended answer. "Yes" meant
accepting the recommendation.

### Round 1

| Q | Question | AI recommended |
| :- | :- | :- |
| Q1 | Bring local `main` up to date? | Yes: back up `tests/test2.py`, discard the m2e noise, fast-forward |
| Q2 | Undo `ca4c3cf`'s m2e state, or accept it? | (a) Remove it, ignore the files, and do #7's editor setting |
| Q3 | Close #4 and #5? | Yes, pointing to #12 and #13 |
| Q4 | Run the unit tests in CI? | Yes, one step after `./build.sh` |
| Q5 | Pin the Python dependencies? | Yes, a full `pip freeze` on Python 3.12 |
| Q6 | Move the clone out of Google Drive? | Yes, unless the course requires Drive |
| Q7 | "Exam-Slot Assignment" against _Avoid_ "slot"? | Keep the brief's name; one Glossary line saying its slot is a Batch |
| Q8 | Delete branches already on `main`? | Local branches and worktrees only |
| Q9 | Scope of this pass? | Setup only: no known limitations, no root BESSER folders |

> Q1 yes. Q2 (a). Q3 yes. Q4 yes. Q5 yes. Q6 no. Q7 yes. Q8 yes, even shared remote branches that I pushed. Q9 ok. One question, should the root of the repo have an AGENTS.md ?

The AI answered that the root `AGENTS.md` already existed on `origin/main`
(`3d2f90f`) and was the right size, but lacked a commit rule (Q10).

### Round 2

| Q | Question | AI recommended |
| :- | :- | :- |
| Q10 | Add a commit rule to the root `AGENTS.md`? | Yes: commit only intended files, editor and IDE state stays out |
| Q11 | How to stop the language server changing the bundles (#7)? | `java.import.exclusions` += `**/emf/**` in `.vscode/settings.json` at the root and in `emf/`; Alef checks Antigravity |
| Q12 | Where do the results tables come from? | First table from CI on the PR; second table marked as measured before pinning |
| Q13 | How do the changes ship? | One PR, commits split at the `emf/` boundary, pushed only after Alef's OK |
| Q14 | Delete these branches and worktrees? | Yes, including the locked worktrees, with `--force` |

> Q10 yes. Q11 yes. Q12 yes. Q13 yes. Q14 yes.

### After the rounds

> Go ahead and push. Why the permission check blocked you? I will open emf with Antigravity now

> I already opened antigravity on the main checkout. Should I switch to the worktree?

> I closed Antigravity and opened it in the worktree

> I closed antigravity

> I opened antigravity again. Java: Ready

> I opened the root now

> I merged it. Now do your thing

> I closed #4 and #5. Remember to add this session to the ai log

> You can push directly to main the addition

## 4. Where Alef changed the plan

| Q | AI recommended | Alef decided |
| :- | :- | :- |
| Q6 | Move the clone out of Google Drive | Keep it in Drive |
| Q8 | Delete local branches only | Also the remote branches Alef pushed |
| — | — | Asked whether the root should have an `AGENTS.md`, which became Q10 |

All other recommendations were accepted as given.

## 5. What the AI did

1. Fast-forwarded local `main` after backing up `tests/test2.py`, then put the
   file back on disk, untracked.
2. Removed the three worktrees, the ten local branches and Alef's ten remote
   branches.
3. Opened [#22](https://github.com/Alef-Keuffer/qmde/pull/22) from a new
   worktree, with commits that never mix `emf/` with other paths:
   - the bundles' `.project` files back to before `ca4c3cf`, the m2e prefs and
     `pom.tycho` removed and ignored;
   - `.vscode/settings.json` (root and `emf/`) keeping the Java language server
     off `emf/`;
   - the commit rule in the root `AGENTS.md`;
   - a CI step running the `python/` and `tools/` unit tests;
   - `requirements.txt` pinned with `pip freeze`;
   - the first results table in `emf/CONTEXT.md` from CI with the pins (same
     schedules, costs and optimality; path, clique and semester probabilities
     moved), and a note on the second table;
   - the Glossary line under Batch.
4. Fixed the language-server settings after Alef's Antigravity check failed
   (see 6).
5. After the merge: fast-forwarded `main`, removed the PR worktree and branch,
   and cleared Antigravity's Java cache for the main checkout's `emf/`.
6. Wrote this record and the AI log entry.

## 6. Mistakes and checks

- **Exclusion pattern:** `**/emf/**` did not stop the import. Alef's first
  Antigravity check on the worktree showed all five `.project` files changed
  again, even the three bundles without a `pom.xml`. The pattern matches
  folders inside `emf/` but not `emf` itself, so the language server imported
  `emf/pom.xml` and, through its modules, every bundle. The fix adds `**/emf`
  and `java.import.maven.enabled: false`. The AI also had to delete the
  language server's cached import before retesting.
- **Testing in the wrong checkout:** Alef first opened Antigravity on the main
  checkout, which lacked the new settings and already had the m2e nature, so
  `git status` there would prove nothing. Antigravity still rewrote
  `pom.tycho` there (and deleted it on close); the AI restored it.
- **Branch count:** the AI first said 11 local branches; it was 10.
- **`tools/headless-problems` hung** for 11 minutes on the first run: an Xtext
  `ConcurrentModificationException` during the headless build left Eclipse
  unable to exit, and the tool has no timeout. A rerun passed in seconds.
- **CI watcher:** the AI's first wait ended before GitHub had registered the
  PR's runs; it waited again until both had started.
- **Permission check:** Claude Code's auto mode blocked `gh issue close` as an
  external write, so Alef closed #4 and #5.
- **Checks:** both Antigravity cases (the worktree's `emf/`, then its root) left
  `git status` clean with no language-server files; `tools/headless-problems`
  exit 0 on the branch; 4 + 4 unit tests passing locally and in CI; `emf` and
  `emf-ide` green on #22.
- **Not checked:** whether the remaining gap between local and CI results is
  the platform; other editors (plain VS Code, IntelliJ).
