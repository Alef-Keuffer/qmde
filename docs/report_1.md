Group: G3
Problem: A3 (Optimisation with QAOA - Exam-slot assignment)

## Explanation of the problem

In the Exam-Slot Assignment Problem, a university needs to schedule final exams for a set of courses into a limited number of time slots so that no student has two exams at the same time.

As there may be cases with no feasible solution (where no configuration allows every student to take every exam they need), weights are added to each exam to establish priorities and assign a penalty for missing an exam. In these cases, the goal is to minimize the penalties for missed exams (i.e., the lowest possible weights).

## Tables with identified classes

### Problem

| Concept |  Intrinsic Properties |  Extrinsic Properties  |
|---|---|---|
| Student |  Name: String |  Has to do 0 or more exams. |
| Exam  |  Name: String<br> Weight: integer |  Must have one or more students.<br> Occupies exactly one time slot (or 0 before being assigned a TimeSlot). |
| TimeSlot  | Id: uint  | Has 0 or more exams.  |

### Solution

| Concept |  Intrinsic Properties |  Extrinsic Properties  |
|---|---|---|
| QUBO | Offset: Real | Arbitrary number of variables, linear terms, quadratic terms, and penalties |
| Variable | Index: Integer <br> Label: String | |
| LinearTerm | Coefficient: Real | One variable, zero or one penalty |
| QuadraticTerm | Coefficient: Real | Two variables, zero or one penalty |
| Penalty | Weight: Real <br> Constraint: String | Arbitrary number of terms it generates |

## Explanation of example problem

- Reduced the number of exams to a minimum (k=3) because the solution model is huge.


## Design decisions

- Adding weights to the problem to increase complexity; this might be removed later.


## References

- Lucas A (2014) Ising formulations of many NP problems. Front. Physics 2:5. doi: 10.3389/fphy.2014.00005
