"""Transform an exam scheduling problem model into a QUBO object model."""

import runpy
from itertools import combinations
from pathlib import Path
from typing import Any

from besser.BUML.metamodel.object import ObjectModel


METAMODELS_DIR = Path(__file__).resolve().parent.parent / "metamodels"
ASSIGNMENT_PENALTY_WEIGHT = 1.0
CONFLICT_PENALTY_WEIGHT = 1.0


def _attribute_value(obj: Any, attribute_name: str) -> Any:
    for slot in obj.slots:
        if slot.attribute.name == attribute_name:
            return slot.value.value
    raise ValueError(
        f"Object {obj.name!r} has no value for required attribute {attribute_name!r}"
    )


def _load_solution_dsl(problem_model: ObjectModel) -> dict[str, Any]:
    return runpy.run_path(
        str(METAMODELS_DIR / "solution_dsl.py"),
        init_globals={"object_model": problem_model},
    )


def transform_problem_to_qubo(problem_model: ObjectModel) -> ObjectModel:
    """Build the QUBO object model for an exam scheduling problem."""
    solution_dsl = _load_solution_dsl(problem_model)
    problem_objects = list(problem_model.objects)

    problems = [obj for obj in problem_objects if obj.classifier.name == "Problem"]
    if len(problems) != 1:
        raise ValueError(
            f"Expected exactly one Problem object, found {len(problems)}"
        )

    batch_count = _attribute_value(problems[0], "nBatches")
    if isinstance(batch_count, bool) or not isinstance(batch_count, int) or batch_count < 1:
        raise ValueError("Problem.nBatches must be a positive integer")

    exams = [obj for obj in problem_objects if obj.classifier.name == "Exam"]
    if not exams:
        raise ValueError("The problem must contain at least one exam")

    students_by_exam = {exam: set() for exam in exams}
    for link in problem_model.links:
        if link.association.name != "Exam_Student":
            continue
        linked_objects = {
            end.object.classifier.name: end.object for end in link.connections
        }
        exam = linked_objects.get("Exam")
        student = linked_objects.get("Student")
        if exam in students_by_exam and student is not None:
            students_by_exam[exam].add(student)

    exam_names = {exam: _attribute_value(exam, "name") for exam in exams}
    if any(not isinstance(name, str) or not name for name in exam_names.values()):
        raise ValueError("Every exam must have a non-empty name")

    exams.sort(
        key=lambda exam: (
            exam_names[exam],
            tuple(
                sorted(
                    _attribute_value(student, "name")
                    for student in students_by_exam[exam]
                )
            ),
        )
    )
    exam_indices = {exam: index for index, exam in enumerate(exams)}

    QUBO = solution_dsl["QUBO"]
    Variable = solution_dsl["Variable"]
    LinearTerm = solution_dsl["LinearTerm"]
    QuadraticTerm = solution_dsl["QuadraticTerm"]
    Penalty = solution_dsl["Penalty"]

    variables_by_exam_batch: dict[Any, dict[int, Any]] = {}
    variables: set[Any] = set()
    linear_terms: set[Any] = set()
    quadratic_terms: set[Any] = set()
    objects: set[Any] = set()

    qubo = QUBO("exam_scheduling_qubo").attributes(
        offset=len(exams) * ASSIGNMENT_PENALTY_WEIGHT
    ).build()
    assignment_penalty = Penalty("one_batch_per_exam").attributes(
        weight=ASSIGNMENT_PENALTY_WEIGHT,
        constraint="Each exam is assigned to exactly one batch",
    ).build()
    conflict_penalty = Penalty("shared_student_conflicts").attributes(
        weight=CONFLICT_PENALTY_WEIGHT,
        constraint="Exams with shared students cannot use the same batch",
    ).build()
    penalties = {assignment_penalty, conflict_penalty}
    objects.update((qubo, assignment_penalty, conflict_penalty))

    next_index = 0
    linear_terms_by_penalty: dict[Any, set[Any]] = {
        assignment_penalty: set(),
        conflict_penalty: set(),
    }
    quadratic_terms_by_penalty: dict[Any, set[Any]] = {
        assignment_penalty: set(),
        conflict_penalty: set(),
    }

    for exam_index, exam in enumerate(exams):
        variables_by_exam_batch[exam] = {}
        for batch in range(batch_count):
            variable = Variable(f"x_{exam_index}_b{batch}").attributes(
                index=next_index,
                label=f"x_{exam_index}_b{batch}_{exam_names[exam]}",
            ).build()
            next_index += 1
            variables_by_exam_batch[exam][batch] = variable
            variables.add(variable)
            objects.add(variable)

            linear_term = LinearTerm(f"linear_{variable.name}").attributes(
                coefficient=-ASSIGNMENT_PENALTY_WEIGHT
            ).build()
            variable.linearterm = linear_term
            linear_terms.add(linear_term)
            linear_terms_by_penalty[assignment_penalty].add(linear_term)
            objects.add(linear_term)

        exam_variables = variables_by_exam_batch[exam]
        for first_batch, second_batch in combinations(range(batch_count), 2):
            term = QuadraticTerm(
                f"one_hot_{exam_index}_{first_batch}_{second_batch}"
            ).attributes(coefficient=2 * ASSIGNMENT_PENALTY_WEIGHT).build()
            term.variable = {
                exam_variables[first_batch],
                exam_variables[second_batch],
            }
            quadratic_terms.add(term)
            quadratic_terms_by_penalty[assignment_penalty].add(term)
            objects.add(term)

    for first_exam, second_exam in combinations(exams, 2):
        shared_student_count = len(
            students_by_exam[first_exam] & students_by_exam[second_exam]
        )
        if not shared_student_count:
            continue

        first_index = exam_indices[first_exam]
        second_index = exam_indices[second_exam]
        for batch in range(batch_count):
            term = QuadraticTerm(
                f"conflict_{first_index}_{second_index}_b{batch}"
            ).attributes(
                coefficient=CONFLICT_PENALTY_WEIGHT * shared_student_count
            ).build()
            term.variable = {
                variables_by_exam_batch[first_exam][batch],
                variables_by_exam_batch[second_exam][batch],
            }
            quadratic_terms.add(term)
            quadratic_terms_by_penalty[conflict_penalty].add(term)
            objects.add(term)

    qubo.variable = variables
    qubo.linearterm = linear_terms
    qubo.quadraticterm = quadratic_terms
    qubo.penalty = penalties
    for penalty in penalties:
        penalty.linearterm = linear_terms_by_penalty[penalty]
        penalty.quadraticterm = quadratic_terms_by_penalty[penalty]

    return ObjectModel(
        name=f"{problem_model.name}_QUBO",
        objects=objects,
    )
