"""Tests for the report's generator: python3 -m unittest discover -s docs/report_2"""
import json
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
""")
        self.assertEqual(generate.citations(path), [
            ("rule R", "[Paper §5.2, Fig. 3]: the graph G, one node per exam [Glover §4.2]."),
            ("lazy rule NewBatch", "[Paper §5.3, Eq. (4)]: batch k."),
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
''')
        self.assertEqual(generate.citations(path), [
            ("penalty", 'A: the largest weight plus one. [Lucas §4.2]: "Choosing B < A".'),
            ("qaoa", "[Farhi Eq. (5)]: |s>"),
            ("qaoa", "[Farhi Eq. (6)]: p alternating layers [Lucas §2.3]."),
            ("expected_energy", "[Farhi Eq. (7)]: F_p."),
        ])


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
        tikz = generate.class_diagram(generate.MODELS / "problem.ecore")
        self.assertIn("weight: EDouble = 1.0", tikz)
        self.assertIn(r"\textit{inv} positiveWeight", tikz)
        self.assertIn(r'\path (Problem) edge[contain, "exams 0..*" role] (Exam);', tikz)
        self.assertIn(r'\path (Exam) edge[reference, "students 1..*" role] (Student);', tikz)

    def test_class_diagram_shows_enumerations(self):
        tikz = generate.class_diagram(generate.MODELS / "solverconfig.ecore")
        self.assertIn(r"\textbf{Optimizer}", tikz)
        self.assertIn(r"COBYLA\\NELDER\_MEAD\\POWELL", tikz)
        self.assertIn("method: Method = QAOA", tikz)


if __name__ == "__main__":
    unittest.main()
