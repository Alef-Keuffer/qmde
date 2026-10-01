# Background and Goal

Quantum computers promise advantages for some classes of problems, such as combinatorial optimization, simulation of physical systems, search, sampling and certain machine-learning tasks. However, programming them today means working almost directly at the level of circuits: qubits, gates and measurements. This is the equivalent of writing assembly, and it creates a large gap between the people who have the problems (logisticians, financial analysts, physicists, data scientists) and the people who can write quantum programs.

Model-Driven Engineering (MDE) is well-suited to closing this gap. A domain expert should be able to state what the problem is in a domain-specific language (DSL), and a chain of model transformations, grounded in the published formulations for that domain, should derive how to solve it on a quantum computer, ending in executable code.

The goal of this project is to design and implement such a chain for one class of problems: a DSL (metamodel) for formulating problems of that class, a DSL (metamodel) for the solution, model-to-model (M2M) transformations between them, and model-to-text (M2T) transformations that generate Python code for Qiskit.

# Overview of the Transformation Chain

Splitting the chain into two M2M steps keeps each transformation small, testable and traceable to the literature: T1 follows the domain formulation (e.g. how a scheduling problem becomes a Quadratic Unconstrained Binary Optimization (QUBO)), and T2 follows the algorithm construction (e.g. how a QUBO becomes a Quantum Approximate Optimization Algorithm (QAOA) circuit).

Some choices are not part of the problem itself but of how it is solved, for example, the QAOA depth, penalty weights, the encoding of integer variables, or the number of Trotter steps. These must be modelled explicitly, either in the problem DSL or in a small separate solver configuration model/DSL that is an extra input to the transformations. They must not be hard-coded in the transformations. 

| Layer | Artefact | Produced by |
| :---- | :---- | :---- |
| 1\. Problem DSL | Abstract syntax (metamodel \+ OCL) for describing problem instances of your class of problems | Us |
| 2\. Solution DSL | A mathematical formulation of the problem, e.g., QUBO/Ising, Boolean formula, Pauli-sum Hamiltonian, probability tables (depends on the class of problems) | Us M2M transformation T1 from Problem DSL) |
| 3\. Quantum DSL | An instance of your quantum circuit metamodel: registers, gates, parameters, measurements, repeated layers | Existent M2M transformation T2 from Solution DSL (Part II) |
| 4\. Code | Runnable Qiskit Python | Existent M2T transformation T3 from Quantum DSL (by BESSER) |
| 5\. Results | Execution on a simulator, compared against a classical baseline | Generated code \+ our validation scripts |

![][image1]

# Classes of Problems

| \# | Class | Intermediate model | Quantum target |  |
| :---- | :---- | :---- | :---- | :---- |
| A | Combinatorial optimisation (graph problems, knapsack, partitioning, portfolio, scheduling) | QUBO / Ising | QAOA with a fixed angle schedule |  |
| B | Constraint satisfaction and search (SAT, Sudoku, N-queens, puzzles) | Boolean formula / CNF | Grover (synthesised oracle \+ diffuser) |  |
| C | Probabilistic reasoning (Bayesian networks) | Factorised joint distribution (CPTs) | State preparation with multi-controlled rotations \+ sampling |  |
| D | Reversible arithmetic (integer expressions, comparisons) | Reversible arithmetic netlist | Adder and comparator circuits (ripple-carry, QFT-based) |  |

# Tools

BESSER includes a quantum circuit metamodel (registers, gates with control and anti-control qubits, measurements, sub-circuits), a graphical circuit editor in the BESSER Web Modeling Editor, and a Qiskit code generator with the Qiskit Aer simulator.

A fork of Besser available at https://github.com/jacomecunha/BESSER, will be used, as updates may be necessary during development.

# Modelling Domain Analysis

At least three concrete problem instances of different kinds and sizes will be collected; these will become the test cases. From this analysis, two lists of concepts will be built: one for each language (problem and solution). For each concept, its attributes will be defined (e.g. weight, capacity, rotation angle) and its connections to other concepts (e.g. an edge connects two nodes; a gate acts on one or more qubits).

This list of concepts is a deliverable. Also, it shall be recorded, for each concept of the problem DSL, which element of the solution DSL model it maps to and according to which reference. This is the seed of transformation T1.

# Modelling Language Design

Using the concept lists, define the two metamodels. Not all constraints can be expressed in the metamodel, so OCL is used to bring the metamodels closer to reality. Examples: every edge refers to existing nodes; capacities are positive; qubit indices are within the register size; the control and target qubits of a controlled gate are distinct; every parameter used in a gate is declared.

# Deliverables I

1. [ ] The two lists of concepts for the two languages (problem DSL and solution DSL), including attributes, connections and the mapping to references.
2. [ ] The metamodel of the problem DSL, with OCL constraints.
3. [ ] The metamodel of the solution DSL, with OCL constraints.
4. [ ] Example models for one small problem instance, built by hand: the problem model and the corresponding solution model.
5. [ ] A very short report (about 2 pages, hand-written, not generated ;) about what inspired your metamodels (e.g., which references you used) and the justifications you find necessary, so we can better understand your options.
6. [ ] The LLM usage log for this part (see Use of LLMs).

# Model-to-Model Transformations

Implementation of transformation T1 (problem model → solution model) and transformation T2 (solution model → quantum model). Each transformation rule must be traceable to the reference it implements (i.e., by citing it in a comment next to the rule and in the report). The solver configuration shall be taken into account (depth, penalty weights, encodings, number of iterations or steps). Any logic needed to solve the problem, such as decoding measured bitstrings back into a schedule, a colouring or a portfolio, must also be derived from the models and not added by hand afterwards.

# Model-to-Text Transformation

Using the BESSER generator, from the quantum model (and, where needed, the problem and configuration models), generate:

- Qiskit Python: a runnable script that builds the circuit, runs it on the Aer simulator, runs the classical optimisation loop for variational algorithms, and prints the result in domain terms.

Generated code must not be edited by hand. If something is wrong, fix the models or the transformations.

# Validation

For each test instances (at least three, small enough to simulate, roughly up to 20 qubits), compare the quantum result against a classical baseline: brute force, a classical solver, exact diagonalisation or exact inference, depending on the class. A metric suited to the class or problems shall be reported, such as the probability of measuring an optimal solution, the approximation ratio, the energy error or the classification accuracy.

# Deliverables II

1. [ ] The M2M transformations T1 and T2, and use the M2T generators for Qiskit Python.
2. [ ] A fully working demonstration: from at least three problem specifications written in your DSL to generated code, execution and results in domain terms, reproducible from the repository with a single documented command.
3. [ ] The validation results against the classical baseline (find a classical implementation to compare against).
4. [ ] A small report (about 2 pages) explaining the transformations and their references, the validation results and the limitations of your approach.
5. [ ] The LLM usage log for this part

# Problem classes

## Graph Optimisation

| Aspect | Description |
| :---- | :---- |
| Example problems | MaxCut, weighted MaxCut, minimum vertex cover, maximum independent set, graph colouring. |
| The DSL expresses | Graphs (nodes, edges, weights), the problem to solve on them, and optionally named node groups. |
| Intermediate model | QUBO / Ising model: variables, linear and quadratic coefficients, offset. |
| Quantum target | QAOA with configurable depth p; classical optimiser loop; decoding bitstrings into cuts, covers or colourings. |
| Minimum scope | MaxCut and one other problem on graphs of up to \~12 nodes. |
| Starting references | A. Lucas, “Ising formulations of many NP problems”, Frontiers in Physics, 2014\. E. Farhi, J. Goldstone, S. Gutmann, “A Quantum Approximate Optimization Algorithm”, arXiv:1411.4028, 2014\. |

## Constrained Scheduling and Allocation

| Aspect | Description |
| :---- | :---- |
| Example problems | Knapsack, bin packing, job-shop scheduling, simple timetabling or shift assignment. |
| The DSL expresses | Jobs or items, resources, capacities, time slots, hard constraints and soft preferences. |
| Intermediate model | QUBO with explicit penalty terms (keeping track of which constraint each term comes from), including slack variables for inequalities. |
| Quantum target | QAOA; decoding into a schedule and checking feasibility. |
| Minimum scope | Knapsack plus one scheduling-type problem, with automatically computed penalty weights. |
| Starting references | F. Glover, G. Kochenberger, Y. Du, “Quantum Bridge Analytics I: a tutorial on formulating and using QUBO models”, 4OR, 2019\. S. Hadfield et al., “From the Quantum Approximate Optimization Algorithm to a Quantum Alternating Operator Ansatz”, Algorithms, 2019\. A. Lucas (2014). |

## **B. Constraint Satisfaction and Search** {#b.-constraint-satisfaction-and-search}

| Aspect | Description |
| :---- | :---- |
| Example problems | SAT, small Sudoku (4×4), N-queens, logic puzzles, exact cover. |
| The DSL expresses | Variables with finite domains and logical or arithmetic constraints over them. |
| Intermediate model | Boolean formula (e.g. CNF) over binary-encoded variables. |
| Quantum target | Grover search: oracle synthesised from the formula (with ancillas and uncomputation), diffuser, and number of iterations derived from the problem size. |
| Minimum scope | SAT formulas and one puzzle type, on up to \~12 search qubits. |
| Starting references | L. Grover, “A fast quantum mechanical algorithm for database search”, STOC, 1996\. M. Boyer, G. Brassard, P. Høyer, A. Tapp, “Tight bounds on quantum searching”, Fortschritte der Physik, 1998\. Nielsen & Chuang \[9\], ch. 6\. |

## Probabilistic Reasoning

| Aspect | Description |
| :---- | :---- |
| Example problems | Small Bayesian networks (e.g. the classic “sprinkler” or medical-diagnosis examples). |
| The DSL expresses | Random variables and their values, parent relations, conditional probability tables, queries and evidence. |
| Intermediate model | Factorised joint distribution with binary-encoded variables. |
| Quantum target | State preparation with (multi-)controlled rotations; sampling; rejection sampling for queries with evidence. |
| Minimum scope | Binary variables, networks of up to \~8 nodes, marginal queries. |
| Starting references | G. H. Low, T. J. Yoder, I. L. Chuang, “Quantum inference on Bayesian networks”, Physical Review A, 2014\. S. E. Borujeni et al., “Quantum circuit representation of Bayesian networks”, Expert Systems with Applications, 2021\. |

## Reversible Arithmetic

| Aspect | Description |
| :---- | :---- |
| Example problems | Integer expressions, comparisons, modular addition; arithmetic sub-circuits used in oracles. |
| The DSL expresses | Typed integer variables with bit widths, expressions and assignments. |
| Intermediate model | Reversible netlist (adders, comparators) with explicit ancilla management. |
| Quantum target | Ripple-carry and QFT-based adders; composition into larger arithmetic circuits. |
| Minimum scope | Addition, subtraction and comparison of n-bit integers. |
| Starting references | V. Vedral, A. Barenco, A. Ekert, “Quantum networks for elementary arithmetic operations”, Physical Review A, 1996\. T. Draper, “Addition on a quantum computer”, arXiv:quant-ph/0008033, 2000\. S. Cuccaro et al., “A new quantum ripple-carry addition circuit”, arXiv:quant-ph/0410184, 2004\. |




