"""Convert an exam scheduling problem instance to a QUBO object model."""

import argparse
import runpy
from pathlib import Path

from besser.BUML.metamodel.object import ObjectModel

if __package__:
    from .transformations.transformation1 import transform_problem_to_qubo
else:
    from transformations.transformation1 import transform_problem_to_qubo


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
    return convert_problem_to_qubo(load_problem_instance(example))


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
        qubo_model = run_pipeline(args.example)
    except (FileNotFoundError, TypeError, ValueError) as error:
        parser.error(str(error))

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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
