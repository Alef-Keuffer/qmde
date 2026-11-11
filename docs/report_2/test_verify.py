"""Tests for the prose checker: python3 -m unittest discover -s docs/report_2"""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import verify


class ClaimsTest(unittest.TestCase):

    def test_sentences_items_captions_and_rows_outside_placeholders(self):
        tex = r"""\documentclass{article}
\begin{document}
\section{Strategy}\label{sec:s}
A Problem has batches \cite[§5.2, Fig. 3]{Paper}.\sidenote{A note.} Farhi et al.\ maximise theirs. % Not a claim.
pyqubo compiles $H$:
\[
	H = x.
\]
With $A$ above every weight, it costs less.
\placeholder{the team}{The chain}{Notes. With claims.}
\begin{itemize}[nosep]
	\item One item.
\end{itemize}
\begin{figure}
	\begin{tikzpicture}\node {Not a claim.};\end{tikzpicture}
	\includegraphics[width=\linewidth]{../imgs/chain-1.png}
	\caption{A caption, \texttt{x}.}\label{fig:x}
\end{figure}
\begin{tabular}{@{}lr@{}}
	\toprule
	path & 8 \\
	\bottomrule
\end{tabular}
\end{document}
"""
        self.assertEqual(verify.claims(tex), [
            r"A Problem has batches \cite[§5.2, Fig. 3]{Paper}.",
            "A note.",
            r"Farhi et al.\ maximise theirs.",
            r"pyqubo compiles $H$: \[ H = x.\]",
            "With $A$ above every weight, it costs less.",
            "One item.",
            r"A caption, \texttt{x}.",
            "path & 8",
        ])

    def test_the_prose_of_input_sections_but_not_of_input_generated(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(verify, "HERE", Path(tmp)):
            for name, text in {"sections/a.tex": "% Not a claim.\nIn a.\n\\input{sections/b}\n",
                               "sections/b.tex": "In b, 27\\% of it.\n",
                               "generated/c.tex": "Generated.\n"}.items():
                (Path(tmp) / name).parent.mkdir(exist_ok=True)
                (Path(tmp) / name).write_text(text, encoding="utf-8")
            tex = "\\begin{document}\nFirst.\n\\input{sections/a}\n% \\input{sections/gone}\n" \
                  "\\input{generated/c}\nLast.\n\\end{document}\n"
            self.assertEqual(verify.claims(tex), ["First.", "In a.", r"In b, 27\% of it.", "Last."])


class ProblemsTest(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "code.py").write_text("BASELINE_LIMIT = 10**6  # skip brute force\n", encoding="utf-8")
        notebook = {"cells": [{"execution_count": 15, "source": ["sampler = neal.SimulatedAnnealingSampler()"]}]}
        (self.root / "nb.ipynb").write_text(json.dumps(notebook), encoding="utf-8")
        for patch in (mock.patch.object(verify, "ROOT", self.root),
                      mock.patch.object(verify, "SOURCES", self.root / "sources"),
                      mock.patch.dict(verify.LOCAL, {"Notebook": self.root / "nb.ipynb",
                                                     "Paper": self.root / "no-such.pdf"})):
            patch.start()
            self.addCleanup(patch.stop)

    def test_quotes_that_hold_and_cover_the_numbers(self):
        claim = r"The Baseline stops at $10^6$ schedules (\texttt{code.py}), annealing as \cite[cell 15]{Notebook} does."
        evidence = [{"path": "code.py", "quote": "BASELINE_LIMIT  =  10**6"},
                    {"cite": "Notebook", "quote": "neal.SimulatedAnnealingSampler()"}]
        self.assertEqual(verify.problems(claim, evidence), ([], []))

    def test_a_changed_quote_an_unquoted_number_and_a_missing_path(self):
        claim = r"The Baseline stops at $10^7$ schedules (\texttt{gone/code.py})."
        found, _ = verify.problems(claim, [{"path": "code.py", "quote": "BASELINE_LIMIT = 10**6"},
                                           {"path": "code.py", "quote": "skip exhaustive search"}])
        self.assertEqual(found, ["names gone/code.py, which does not exist",
                                 "quote not in code.py: 'skip exhaustive search'",
                                 "number(s) 7 in none of its quotes"])

    def test_every_cited_reference_quoted_its_locators_not_numbers(self):
        claim = r"Each weight is 1 by default \cites[§5.2, Eq. (3)]{Paper}[cell 15]{Notebook}."
        found, warnings = verify.problems(claim, [{"path": "code.py", "quote": "weight = 1.0"}])
        self.assertIn("quote not in code.py: 'weight = 1.0'", found)
        self.assertIn("cites [Notebook] but quotes nothing from it", found)
        self.assertEqual(warnings, ["[Paper] unchecked: no text of it (sources/Paper.txt)"])
        self.assertFalse([p for p in found if p.startswith("number")])

    def test_unverified_and_nothing_to_check(self):
        self.assertEqual(verify.problems("Both chains follow it.", None), (["unverified"], []))
        self.assertEqual(verify.problems("Both chains follow it.", []), ([], []))


if __name__ == "__main__":
    unittest.main()
