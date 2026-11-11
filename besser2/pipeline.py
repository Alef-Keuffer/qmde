"""Convert an exam scheduling problem instance to a QUBO object model."""

import argparse
import runpy
from pathlib import Path

from besser.BUML.metamodel.object import ObjectModel

if __package__:
    from .transformations.transformation1 import transform_problem_to_qubo
    from .transformations.transformation2 import QuboSolution, solve_qubo
else:
    from transformations.transformation1 import transform_problem_to_qubo
    from transformations.transformation2 import QuboSolution, solve_qubo


ROOT = Path(__file__).resolve().parent
INSTANCES_DIR = ROOT / "instances"
METAMODELS_DIR = ROOT / "metamodels"


def load_problem_instance(example: str) -> ObjectModel:
    """Load an instance by filename stem from besser2/instances."""
    example_name = example[:-3] if example.endswith(".py") else example
    if not example_name or Path(example_name).name != example_name:
        raise ValueError("The example must be a filename stem inside instances/")

    problem_path = METAMODELS_DIR / "problem_dsl_project_new.py"
    instance_path = INSTANCES_DIR / f"{example_name}.py"
    if not instance_path.is_file():
        raise FileNotFoundError(f"Problem instance not found: {instance_path}")

    problem_dsl = runpy.run_path(str(problem_path))
    instance_globals = {
        name: problem_dsl[name] for name in ("Exam", "Student", "Problem")
    }
    instance_globals["ObjectModel"] = ObjectModel
    instance = runpy.run_path(str(instance_path), init_globals=instance_globals)

    problem_model = instance.get("object_model")
    if not isinstance(problem_model, ObjectModel):
        raise TypeError(f"{instance_path} does not define an ObjectModel named object_model")
    return problem_model


def convert_problem_to_qubo(problem_model: ObjectModel) -> ObjectModel:
    """Compatibility wrapper for the QUBO transformation."""
    return transform_problem_to_qubo(problem_model)


def run_pipeline(example: str) -> ObjectModel:
    qubo_model = convert_problem_to_qubo(load_problem_instance(example))
    counts: dict[str, int] = {}
    for obj in qubo_model.objects:
        counts[obj.classifier.name] = counts.get(obj.classifier.name, 0) + 1
    print(
        "Generated QUBO: "
        f"{counts.get('Variable', 0)} variables, "
        f"{counts.get('LinearTerm', 0)} linear terms, "
        f"{counts.get('QuadraticTerm', 0)} quadratic terms, "
        f"{counts.get('Penalty', 0)} penalties"
    )
    print_solution(solve_qubo(qubo_model))
    return qubo_model


def print_solution(solution: QuboSolution) -> None:
    """Print the best QUBO schedules found and whether optimality is proven."""
    solver_name = "Exact QUBO search" if solution.exact else "Simulated annealing"
    optimality = "proven optimal" if solution.exact else "best found; optimality not proven"
    print(
        f"{solver_name} ({solution.variable_count} binary variables; {optimality})"
    )
    print(f"Best QUBO energy: {solution.best_energy:g}")

    candidates = [candidate for candidate in solution.candidates if candidate.is_feasible]
    if candidates:
        print(
            f"Found {solution.feasible_solution_count} best conflict-free "
            "schedule(s)"
        )
    else:
        candidates = list(solution.candidates)
        print("No conflict-free schedule was found among the best assignments.")

    for number, candidate in enumerate(candidates, start=1):
        print(f"Solution {number}:")
        for _, exam_name, batches in candidate.assignments:
            if len(batches) == 1:
                print(f"  {exam_name}: Batch {batches[0] + 1}")
            elif batches:
                batch_list = ", ".join(str(batch + 1) for batch in batches)
                print(f"  {exam_name}: assigned to multiple batches ({batch_list})")
            else:
                print(f"  {exam_name}: unassigned")
        for violation in candidate.violations:
            print(f"  Violation: {violation}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert an exam scheduling instance into a QUBO object model."
    )
    parser.add_argument(
        "example",
        help="filename stem from besser2/instances (for example: object_diagram)",
    )
    args = parser.parse_args(argv)

    try:
        run_pipeline(args.example)
    except (FileNotFoundError, TypeError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
