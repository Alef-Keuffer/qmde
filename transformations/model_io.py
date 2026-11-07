"""Loading and saving B-UML models, and every workaround for the course fork of BESSER.

The transformations know the metamodels, never the instances (slides T6, "Organizing your repository").
Everything that touches BESSER's I/O, and every workaround for a bug of the fork, lives in this module.

Workarounds for the fork jacomecunha/BESSER @ 9cf7a90 (BESSER 7.18.0):
  W1  Part I's solution_dsl.py was exported by the web editor (BESSER 8.2.1) and passes ``metadata=`` to
      ObjectModel, which this version does not accept: load_buml() accepts the argument and drops it.
  W2  project_to_code() crashes when the Project has no metadata: save_models() always gives it one.
  W3  A metamodel loaded twice yields two different Class objects (slides T6, "Two copies of a metamodel"):
      objects are found by class name and links by association-end name (objects_of, linked).
  W4  Part I's problem metamodel makes Exam_TimeSlot 1..1 on the timeSlot end, which an unsolved problem
      cannot satisfy: validate_problem() ignores exactly that error (the solved model written by map_back
      satisfies it).
"""

import contextlib
import functools
import io
import json
import runpy
from pathlib import Path

from besser.BUML.metamodel.object import ObjectModel
from besser.BUML.metamodel.project import Project
from besser.BUML.metamodel.structural import DomainModel, Metadata
from besser.utilities.buml_code_builder.project_builder import project_to_code

ROOT = Path(__file__).resolve().parent.parent
PART_I = ROOT / "metamodels" / "buml"


def load_buml(path) -> dict:
    """Run a B-UML .py file (editor export or project_to_code output) and return its namespace (W1)."""
    original = ObjectModel.__init__

    def accept_metadata(self, name, objects=None, metadata=None):  # W1: metadata is dropped
        original(self, name, objects)

    ObjectModel.__init__ = accept_metadata
    try:
        return runpy.run_path(str(path))
    finally:
        ObjectModel.__init__ = original


@functools.cache
def problem_metamodel() -> DomainModel:
    """Problem DSL of Part I (Exam, Student, TimeSlot), read from metamodels/ and never changed."""
    return load_buml(PART_I / "problem_dsl.py")["domain_model"]


@functools.cache
def solution_metamodel() -> DomainModel:
    """Solution DSL of Part I (QUBO, Variable, LinearTerm, QuadraticTerm, Penalty), read from metamodels/."""
    return load_buml(PART_I / "solution_dsl.py")["domain_model"]


def classes(domain_model: DomainModel, *names: str) -> tuple:
    """The classes of a metamodel, by name, in the order asked."""
    by_name = {c.name: c for c in domain_model.get_classes()}
    return tuple(by_name[name] for name in names)


def objects_of(model: ObjectModel, class_name: str) -> list:
    """The objects of one class, sorted by object name so that every run is deterministic (W3)."""
    return sorted((o for o in model.objects if o.classifier.name == class_name), key=lambda o: o.name_)


def linked(obj, end_name: str) -> list:
    """The objects linked to obj through the association end called end_name, sorted by name (W3)."""
    return sorted({le.object for le in obj.link_ends() if le.association_end.name == end_name},
                  key=lambda o: o.name_)


def validate_problem(model: ObjectModel) -> list:
    """Errors of a problem model, except the Exam_TimeSlot multiplicity an unsolved problem breaks (W4)."""
    errors = model.validate(raise_exception=False)["errors"]
    return [e for e in errors
            if not ("association end 'timeSlot' of association 'Exam_TimeSlot'" in e and "(found 0 links)" in e)]


def to_json(model: ObjectModel) -> dict:
    """A plain JSON view of an object model (objects, attribute values, links), for inspection only."""
    objects = [{"name": o.name_, "class": o.classifier.name,
                "attributes": {s.attribute.name: s.value.value for s in o.slots}}
               for o in sorted(model.objects, key=lambda o: o.name_)]
    links = sorted(({"association": link.association.name,
                     "ends": {c.association_end.name: c.object.name_ for c in link.connections}}
                    for link in model.links),
                   key=lambda link: (link["association"], sorted(link["ends"].items())))
    return {"name": model.name, "objects": objects, "links": links}


def save_models(stem: Path, domain_model: DomainModel, model: ObjectModel, description: str) -> None:
    """Save a model as <stem>.py (B-UML, reloadable with load_buml) and <stem>.json (inspection)."""
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    project = Project(name=model.name, models=[domain_model, model], owner="QMDE group G3",
                      metadata=Metadata(description=description))  # W2
    with contextlib.redirect_stdout(io.StringIO()):  # project_to_code prints a temporary path
        project_to_code(project, str(stem.with_suffix(".py")))
    stem.with_suffix(".json").write_text(json.dumps(to_json(model), indent=2) + "\n", encoding="utf-8")
