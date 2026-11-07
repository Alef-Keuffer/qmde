# LLM Usage Log (Part II)

One entry per significant use. Fields: tool and model, goal, summary of the prompt, what was accepted, and what was wrong and how it was detected and fixed.

---

## 1. Understanding the project and the EMF chain

- **Used by:** Luis
- **Tool and model:** Claude Code (VS Code extension), Claude Opus 5.5
- **Date:** 2026-11-07
- **Goal:** Before contributing to Part II, I had to understand what my colleagues had already built. I used Claude Code to guide me through the EMF chain one step at a time, always using the smallest example (`path`), so I could see what goes into each step and what comes out of it.
- **Summary of the prompt:** I asked it to read the documentation, the design decisions (ADRs) and the main files of the EMF chain, and to explain each part to me in simple terms without changing anything. When the first explanation was too detailed for me, I asked for a simpler guided tour in four steps.
- **What was accepted:** The overall explanation of the chain: how the text file with the problem becomes a model, how conflicts between exams are found, how the Python code is generated, and how that code builds the penalty function and runs the quantum algorithm. It also helped me see how this matches the layers of the assignment, including the part where the professor allowed us to skip the Quantum DSL in the EMF version.
- **What was wrong, how it was detected and fixed:**
  - The version of BESSER installed on my computer was the public one, not the course fork required by the assignment. We noticed it by checking where the folder came from. The fork was then installed separately, and the chain uses that one.
  - The first version of the quantum algorithm had the sign the wrong way around. QAOA was designed to maximize, and we want to minimize the penalty points. With the wrong sign, the results were worse than picking a schedule at random, which is how we noticed it. We fixed it by following the convention of the original QAOA paper.

## 2. Building the Part II chain in BESSER

- **Used by:** Luis
- **Tool and model:** Claude Code (VS Code extension), Claude Opus 5.5
- **Date:** 2026-11-07
- **Goal:** Build the Part II chain in BESSER, in its own folder: from a problem written as a model, to the penalty function, to the quantum circuit, to the generated Qiskit code, to the results, and back to a schedule that a person can read. I wanted to do it step by step so I could follow what was happening at each stage.
- **Summary of the prompt:** I gave it the structure from the course slides and asked it to cite the paper or book behind every rule, to keep every solver choice (weights, number of layers, angles, number of runs) in a configuration model instead of in the code, and to stop after each stage to explain it to me in a few lines.
- **What was accepted:**
  - The design choices, each one checked before it was kept. The most important one is how strong the penalties are: an exam left without a slot must always cost more than a conflict, otherwise the solver can "cheat" by dropping an exam. We checked this by trying every possible schedule.
  - The results: on all five test problems, the best answer of the penalty function is the same as the best answer found by trying every schedule. The quantum algorithm finds the best schedule much more often than random guessing, but less often as the problems get bigger.
  - The tests, after checking that they really catch the typical mistakes: we put each mistake back on purpose and confirmed that the tests failed.
- **What was wrong, how it was detected and fixed:**
  - The decoded results used different names from the ones in the model, which was confusing. We noticed it when reading the results and made the names match.
  - Running the chain twice gave files in a different order each time, so the results looked different even when they were the same. We noticed it with git and fixed it so that every run gives exactly the same files.