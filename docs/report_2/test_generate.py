"""Tests for the report's generator: python3 -m unittest discover -s docs/report_2"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import generate

TMP = tempfile.TemporaryDirectory()  # removed when the tests exit


def written(suffix, text):
    """A temporary file holding text, whose suffix picks the language."""
    path = Path(tempfile.mkdtemp(dir=TMP.name)) / f"source{suffix}"
    path.write_text(text, encoding="utf-8")
    return path


class CitationsTest(unittest.TestCase):

    def test_atl_comment_block_belongs_to_its_rule(self):
        path = written(".atl", """\
-- Paper: the legend, without brackets.
module m;

rule R {
	from
		p : P!P
	to
		-- [Paper §5.2, Fig. 3]: the graph G,
		-- one node per exam [Glover §4.2].
		g : G!G (
			batches <- p.x
		)
}

-- [Paper §5.3, Eq. (4)]: batch k.
lazy rule NewBatch {
}

unique lazy rule Conflict {
	-- [Paper §5.3, Eq. (5)]: one conflict per pair.
}

-- [Lucas §4.2]: after the last rule.
""")
        self.assertEqual(generate.citations(path), [
            ("rule R", "[Paper §5.2, Fig. 3]: the graph G, one node per exam [Glover §4.2]."),
            ("lazy rule NewBatch", "[Paper §5.3, Eq. (4)]: batch k."),
            ("unique lazy rule Conflict", "[Paper §5.3, Eq. (5)]: one conflict per pair."),
            ("module", "[Lucas §4.2]: after the last rule."),
        ])

    def test_template_comment_belongs_to_the_names_assigned_after_it(self):
        path = written(".mtl", """\
      # From here on, no reference.
      # ['['/]Paper §5.3, Eq. (4)] ['['/]Notebook cell 11]: x['['/]i, k] = 1
      x = Array.create('c', (n, m), 'BINARY')

      # ['['/]Paper §5.3, Eq. (10)]: H, fed
      # from the configuration
      A = Placeholder("A")
      H = profit + A * (c1 + c2)
          label="not a name of the section"
""")
        self.assertEqual(generate.citations(path), [
            ("x", "From here on, no reference. [Paper §5.3, Eq. (4)] [Notebook cell 11]: x[i, k] = 1"),
            ("A, H", "[Paper §5.3, Eq. (10)]: H, fed from the configuration"),
        ])

    def test_python_docstring_and_comments_belong_to_the_innermost_function(self):
        path = written(".py", '''\
"""References: Paper = the legend, without brackets."""


def penalty(p):
    """A: the largest weight plus one.
    [Lucas §4.2]: "Choosing B < A"."""
    return 1


def qaoa(p):
    qc.h(0)  # [Farhi Eq. (5)]: |s>
    # [Farhi Eq. (6)]: p alternating
    # layers [Lucas §2.3].
    def expected_energy():
        """[Farhi Eq. (7)]: F_p."""


class Schedule:
    """[Paper §5.5]: the decoded schedule."""

    async def sample(self):
        # [Notebook cell 15]: annealing
        pass
''')
        self.assertEqual(generate.citations(path), [
            ("penalty", 'A: the largest weight plus one. [Lucas §4.2]: "Choosing B < A".'),
            ("qaoa", "[Farhi Eq. (5)]: |s>"),
            ("qaoa", "[Farhi Eq. (6)]: p alternating layers [Lucas §2.3]."),
            ("expected_energy", "[Farhi Eq. (7)]: F_p."),
            ("Schedule", "[Paper §5.5]: the decoded schedule."),
            ("sample", "[Notebook cell 15]: annealing"),
        ])

    def test_python_module_docstring_belongs_to_the_module(self):
        path = written(".py", '"""The runtime [Paper §5.5]."""\n')
        self.assertEqual(generate.citations(path), [("module", "The runtime [Paper §5.5].")])


def result(instance, method, p_optimal, unscheduled=(), cost=0, optimizer="COBYLA"):
    """A results_<name>.json as the generated scripts write it, with only the fields the report reads."""
    return {"instance": instance, "variables": 12,
            "solver": {"method": method, "penalty": None, "seed": 7, "reads": 50, "sweeps": 10000, "depth": 2,
                       "optimizer": optimizer, "max_iterations": 150, "shots": 4096},
            "penalty": 5.0,
            "schedule": {"assignments": [["Algebra", 1]], "unscheduled": list(unscheduled), "cost": cost,
                         "feasible": True, "broken": []},
            "optimal_cost": cost, "optimal": True, "p_optimal": p_optimal, "p_feasible": 1.0,
            "random_p_optimal": 0.00146484375, "random_p_feasible": 0.017822265625}


class ResultsTest(unittest.TestCase):

    def setUp(self):
        self.instances = Path(tempfile.mkdtemp(dir=TMP.name))
        for name, problem in [("1-clique.exam", "clique"), ("1-clique-qaoa.exam", "clique_qaoa"),
                              ("2-path.exam", "path")]:
            (self.instances / name).write_text(f"// a comment\nproblem {problem} batches 3\n", encoding="utf-8")
        self.results = Path(tempfile.mkdtemp(dir=TMP.name))
        for run in [result("path", "QAOA", 0.000244140625, optimizer="NELDER_MEAD"),
                    result("clique_qaoa", "QAOA", 0.0419921875, ["Statistics"], 1.0),
                    result("clique", "ANNEALING", 0.94, ["Statistics"], 1.0)]:
            folder = self.results / run["instance"]
            folder.mkdir()
            (folder / f"results_{run['instance']}.json").write_text(json.dumps(run), encoding="utf-8")

    def test_context_table_lists_each_instance_then_its_twin(self):
        runs = generate.load_runs(self.results, self.instances)
        self.assertEqual(generate.context_results(runs, "https://github.com/o/r/actions/runs/42"), """\
Results with the committed instances and seeds, from CI's `./build.sh` (Linux, the pinned `requirements.txt`), \
[run 42](https://github.com/o/r/actions/runs/42), written here by `docs/report_2/build.sh`; every schedule found is \
feasible and optimal:

| Instance | Variables | Method | Result (cost, unscheduled exams) | Optimal cost (baseline) | P(optimal) | P(feasible) |
|---|---|---|---|---|---|---|
| clique | 12 | annealing, 50 reads × 10000 sweeps | 1, Statistics | 1 | 0.940 | 1.000 |
| clique | 12 | QAOA, depth 2, COBYLA, 150 iterations, 4096 shots | 1, Statistics | 1 | 0.042 | 1.000 |
| path | 12 | QAOA, depth 2, Nelder-Mead, 150 iterations, 4096 shots | 0, none | 0 | 0.00024 | 1.000 |""")

    def test_splice_replaces_only_what_is_between_the_markers(self):
        text = "Intro.\n\n<!-- results:begin -->\nold table\n<!-- results:end -->\n\nThe rest.\n"
        self.assertEqual(generate.splice(text, "new table"),
                         "Intro.\n\n<!-- results:begin -->\n\nnew table\n\n<!-- results:end -->\n\nThe rest.\n")


class MetamodelTest(unittest.TestCase):

    def test_class_diagram_shows_attributes_invariants_and_references(self):
        tikz = generate.class_diagram(*generate.ecore_classes(generate.MODELS / "problem.ecore"))
        self.assertIn("weight: EDouble = 1.0", tikz)
        self.assertIn(r"\textit{inv} positiveWeight", tikz)
        self.assertIn(r'\path (Problem) edge[contain, "exams 1..*" role] (Exam);', tikz)
        self.assertIn(r'\path (Exam) edge[reference, "students 1..*" role] (Student);', tikz)

    def test_class_diagram_shows_enumerations(self):
        tikz = generate.class_diagram(*generate.ecore_classes(generate.MODELS / "solverconfig.ecore"))
        self.assertIn(r"\textbf{Optimizer}", tikz)
        self.assertIn(r"COBYLA\\NELDER\_MEAD\\POWELL", tikz)
        self.assertIn("method: Method = QAOA", tikz)

    def test_besser_class_diagram_shows_both_ends_and_the_whole_of_a_composition(self):
        tikz = generate.class_diagram(*generate.besser_classes(generate.BESSER_METAMODEL_JSON / "solver_config_dsl.json"))
        self.assertIn("conflictWeight: float", tikz)
        self.assertIn(r"\textit{inv} layers\_match\_depth", tikz)
        self.assertIn(r'\path (SolverConfig) edge[contain, "config 1" source role, "layers 1..*" target role] (QAOALayer);',
                      tikz)
        tikz = generate.class_diagram(*generate.besser_classes(generate.BESSER_METAMODEL_JSON / "problem_dsl.json"))
        self.assertIn(r'\path (Exam) edge[association, "exams 0..*" source role, "timeSlot 1" target role] (TimeSlot);',
                      tikz)


GLOSSARY = """\
# Exam-Slot Assignment

Scheduling exams, with a `code` intro that is not rendered.

## Language

### Problem

**Batch**:
One of a fixed number of exam periods; the "slot" in
the problem's name.
_Avoid_: slot, `TimeSlot`

### Solution

**Cost** (of a schedule):
The total weight: x[Exam, Batch] & 100%, in *batches*.
"""


class TermTest(unittest.TestCase):

    def test_plural_follows_the_regular_english_rule(self):
        for term, plural in [("Batch", "Batches"), ("Exam", "Exams"), ("QUBO", "QUBOs"), ("Box", "Boxes"),
                             ("Bus", "Buses"), ("Wish", "Wishes"), ("Penalty", "Penalties"),
                             ("Day", "Days"), ("Conflict Graph", "Conflict Graphs"),
                             ("Assignment Variable", "Assignment Variables")]:
            with self.subTest(term=term):
                self.assertEqual(generate.plural(term), plural)

    def test_term_table_maps_each_term_and_its_plural_to_its_entry(self):
        self.assertEqual(generate.glossary_terms(GLOSSARY), r"""\glossaryterm{batch}{term:batch}
\glossaryterm{batches}{term:batch}
\glossaryterm{cost}{term:cost}
\glossaryterm{costs}{term:cost}""")

    def test_a_plural_that_is_another_term_stops_the_build(self):
        with self.assertRaisesRegex(SystemExit, "GLOSSARY.md: Exams is both a term and a plural"):
            generate.glossary_terms("## Language\n\n### G\n\n**Exam**:\na\n\n**Exams**:\nb\n")

    @unittest.skipUnless(shutil.which("lualatex"), "needs LuaLaTeX, which CI's report job lacks")
    def test_term_links_a_known_term_and_stops_on_an_unknown_one(self):
        """A tiny LuaLaTeX document with the report's own \\term, on a table of one term."""
        folder = Path(tempfile.mkdtemp(dir=TMP.name))
        (folder / "generated").mkdir()
        (folder / "generated/glossary-terms.tex").write_text(
            "\\glossaryterm{batch}{term:batch}\n\\glossaryterm{batches}{term:batch}\n", encoding="utf-8")

        def build(body):
            (folder / "doc.tex").write_text(r"""\pdfvariable compresslevel=0 \pdfvariable objcompresslevel=0
\documentclass{article}
\usepackage{hyperref}
\usepackage{term}
\begin{document}
\tableofcontents
\section{The \term{Batch}}
\begin{figure}\caption{Two \term{batches}.}\end{figure}
\hypertarget{term:batch}{Batch} %s
\end{document}
""" % body, encoding="utf-8")
            env = {**os.environ, "TEXINPUTS": f"{generate.HERE}:"}
            for _ in range(2):  # the second run reads the contents and the bookmarks back
                run = subprocess.run(["lualatex", "-interaction=nonstopmode", "-halt-on-error", "doc.tex"],
                                     cwd=folder, env=env, capture_output=True, text=True)
                if run.returncode:
                    break
            return run

        known = build(r"\term{BATCHES}")
        self.assertEqual(known.returncode, 0, known.stdout[-2000:])
        pdf = (folder / "doc.pdf").read_bytes()
        self.assertEqual(pdf.count(b"/D (term:batch)"), 4)  # contents, heading, caption, text
        self.assertIn(rb"(\376\377\000T\000h\000e\000\040\000B\000a\000t\000c\000h)", pdf)  # bookmark: the text
        unknown = build(r"\term{Slots}")
        self.assertNotEqual(unknown.returncode, 0)
        self.assertIn("Slots", unknown.stdout[unknown.stdout.find("Error"):])


class GlossaryTest(unittest.TestCase):

    def test_groups_entries_and_avoid_lines_in_order(self):
        self.assertEqual(generate.glossary(GLOSSARY), r"""\subsection*{Problem}
\begin{description}
\item[\hypertarget{term:batch}{Batch}] One of a fixed number of exam periods; the \enquote{slot} in the problem's name.\par
{\small\itshape Avoid: slot, \texttt{TimeSlot}}
\end{description}
\subsection*{Solution}
\begin{description}
\item[\hypertarget{term:cost}{Cost} {\normalfont(of a schedule)}] The total weight: x[Exam, Batch] \& 100\%, in \term{batches}.
\end{description}""")

    def test_the_glossary_renders(self):
        self.assertIn(r"\item[\hypertarget{term:batch}{Batch}]",
                      generate.glossary((generate.EMF / "GLOSSARY.md").read_text(encoding="utf-8")))

    def test_markdown_the_glossary_does_not_use_is_rejected(self):
        for name, line in [("a list", "- one"), ("a list", "1. one"), ("a table", "| a | b |"),
                           ("a link", "See [the paper](https://x)."), ("a heading", "#### Deeper"),
                           ("a quote", "> said"), ("emphasis", "a _word_"), ("emphasis", "a **word**"),
                           ("emphasis", "a * b *"), ("emphasis", "a __word__"),
                           ("HTML", "<br>"), ("HTML", "a &amp; b"), ("a code block", "```"), ("a heading", "---"),
                           ("a heading", "==="), ("emphasis", "### A _b_"), ("a link", "**[a](b)**:"),
                           ("text outside an entry", "### G\nstray"),
                           ("an Avoid line before the definition", "**U**:\n_Avoid_: x")]:
            with self.subTest(line=line):
                with self.assertRaisesRegex(SystemExit, f"GLOSSARY.md line \\d+: {name}"):
                    generate.glossary(f"## Language\n\n### G\n\n**T**:\ntext\n{line}\n")


if __name__ == "__main__":
    unittest.main()
