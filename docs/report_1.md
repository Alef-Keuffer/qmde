- **Group:** G3
- **Problem:** A3 (Optimisation with QAOA - Exam-slot assignment)

| \# | Class                                                          | Intermediate model (solution DSL) | Quantum algorithm |
|:---|:---------------------------------------------------------------|:----------------------------------|:------------------|
| A  | Optimisation with QAOA (graph problems, selection, assignment) | QUBO                              | QAOA              |

| \# | Problem (domain of the problem DSL) | Underlying problem                                                      | Complexity · notes                                                                       |
|:---|:------------------------------------|:------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------|
| 3  | Frequency or exam-slot assignment   | Graph colouring with k colours, minimising conflicts (one-hot encoding) | **NP-hard** · k-colourability NP-complete for k ≥ 3; for k \= 2 it is in P, so use k ≥ 3 |

| Layer            | Artefact                                                                                                                                                      | Produced by                                                   |
|:-----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------|
| 1\. Problem DSL  | Abstract syntax (metamodel \+ OCL) for describing problem instances of your class of problems                                                                 | You (Part I)                                                  |
| 2\. Solution DSL | A mathematical formulation of the problem, defined per class in Annex A: QUBO, Boolean formula (CNF), linear integer constraints, or integer linear programme | You (Part I) M2M transformation T1 from Problem DSL (Part II) |

## Explanation of the problem

In the **Exam-Slot Assignment Problem**, a university needs to schedule final exams for a set of courses into a limited number of time slots so that **no student has two exams at the same time**.

As there may be cases with no feasible solution (where no configuration allows every student to take every exam they need), weights are added to each exam to establish priorities and assign a penalty for missing an exam. In these cases, the goal is to minimize the penalties for missed exams (i.e., the lowest possible weights).

## Problem DSL

| Concept  | Intrinsic Properties             | Extrinsic Properties                                                                                        |
|----------|----------------------------------|-------------------------------------------------------------------------------------------------------------|
| Student  | name: String                     | Has to do 0 or more exams.                                                                                  |
| Exam     | name: String<br> weight: integer | Must have one or more students.<br> Occupies exactly one time slot (or 0 before being assigned a TimeSlot). |
| TimeSlot | id: int                          | Has 0 or more exams.                                                                                        |

![](./imgs/problem-dsl-01.png)

### OCL Constraints

Here I made use of Gemini/Argon(low) to ask for what OCL examples made sense for my model, I gave the model input as codified in plantuml.

* **`Unique TimeSlot IDs:`** `Every time slot must have a distinct identifier.`
* **`Non Negative TimeSlot IDs`**
* **`Unique Exam Names:`** `No two exams should have the exact same course/subject name.`
* **`Non-Empty Attributes:`** `Names and IDs cannot be empty.`

> Uniqueness can't be checked correctly with this version of B-OCL.

This is something I also figured out using AI:

![ai-trying-to-run-with-uniqueness-constraint](./imgs/7dd2b17f-4c92-4af5-9e28-3d293b139ebc.png)

I also used AI to get a workaround working locally which I can show the professor if he is interested:

![](./imgs/44ee0859-fee5-4451-b532-e86407fa3587.png)

## Solution DSL

| Concept       | Intrinsic Properties                 | Extrinsic Properties                                                        |
|---------------|--------------------------------------|-----------------------------------------------------------------------------|
| QUBO          | Offset: Real                         | Arbitrary number of variables, linear terms, quadratic terms, and penalties |
| Variable      | Index: Integer <br> Label: String    |                                                                             |
| LinearTerm    | Coefficient: Real                    | One variable, one penalty                                           |
| QuadraticTerm | Coefficient: Real                    | Two variables, zero or one penalty                                          |
| Penalty       | Weight: Real <br> Constraint: String | Arbitrary number of terms it generates                                      |

![](./imgs/solution-dsl-01.png)

The solution DSL is the language used to describe the mathematical formulation of the problem as a QUBO (Quadratic Unconstrained Binary Optimization). A model in this language represents a cost function

```
f(x) = c + Σ aᵢxᵢ + Σ bᵢⱼxᵢxⱼ, (compact form)
```

The central concept is the QUBO, which represents the whole function. It stores the offset (the c in the formula), the constant value that is always paid regardless of the variables, and it owns all the other elements: variables, linear terms, quadratic terms and penalties. If the QUBO is removed, all of these elements cease to exist.

Each Variable represents a yes-or-no decision, meaning that each variable xᵢ can only be 0 or 1. In our problem, it corresponds to “placing exam X in slot Y” (for example, A@1 for x0 and A@2 for x1).

A LinearTerm represents a term aᵢxᵢ of the formula. It has a coefficient and is linked to exactly one variable: its coefficient is added to the cost when that variable is 1. In our problem, every linear term comes from a penalty, so each one is linked to exactly one penalty.

A QuadraticTerm represents a term bᵢⱼxᵢxⱼ. It has a coefficient and is linked to exactly two distinct variables: the coefficient is only added to the cost when both are 1. It is linked to zero or one penalty. When it is linked, it comes from the rule that each exam is placed in exactly one slot, and it connects two slots of the same exam. When it is not linked, it comes from the objective function: it represents a conflict between two exams that share students, placed in the same slot, and its coefficient is the number of those students. Note that, for the system to prefer a conflict between two exams in the same slot over leaving an exam without a slot, the penalty weight λ must be larger than the sum of the conflict coefficients of any single exam. Pairs of variables without a quadratic term have a zero coefficient and are not stored.

A Penalty represents a constraint of the problem. It stores the weight (λ, the cost of violating the rule) and a description of the constraint. The Penalty does not take part in the cost calculation directly. Its role is traceability: it is linked to every term it generated, so for each term it is possible to know which constraint it came from.

## Example models for one small problem instance

A small department must schedule 3 exams into 3 time slots (Mon 9:00, Mon 14:00, Tue 9:00). Several students sit more than one exam, and no student can sit two exams in the same time slot.

We first attempted 4 exams, but had to reduce the number to 3 (k=3) because the solution model was growing exponentially. It had around 100 objects with 4 exams, but around 30 with only 3.

### Students and exams

| Student | Exams              |
|---------|--------------------|
| Alice   | Math, Physics      |
| Bob     | Physics, Chemistry |
| Carla   | Math               |
| David   | Chemistry          |
| Eva     | Physics            |

### Exam weights

| Exam      | weight |
|-----------|--------|
| Math      | 6      |
| Physics   | 4      |
| Chemistry | 3      |

### Goal

Assign each exam to exactly one of the 3 time slots so that the number of conflicts (pairs of exams sharing a student and placed in the same slot) is minimized, ideally zero.

### Conflict graph (derived from the data)

Two exams are connected if at least one student sits both:
- Physics - Chemistry (Bob)
- Physics - Math (Alice)

The graph-coloring instance has vertices representing exams, edges representing shared students, and colors representing time slots. Since there are 3 time slots, the number of colors is (k=3). This satisfies the condition (k ≥ 3), under which the general graph (k)-colorability decision problem is NP-complete.

### A valid solution

| Exam      | Timeslot  |
|-----------|-----------|
| Math      | Mon 9:00  |
| Physics   | Mon 14:00 |
| Chemistry | Mon 9:00  |

### Problem instance

![](./imgs/problem-instance-01.png)

### Solution instance

![](./imgs/solution-instance-01.png)

## Design decisions

- After first modeling the simplest form of the problem and talking with Professor Jácome, we decided that the models seemed too simple. We added exam weights to increase the problem's complexity; this might be removed later, depending on the problem's future complexity.

## References

- Lucas A (2014) Ising formulations of many NP problems. Front. Physics 2:5. doi: 10.3389/fphy.2014.00005