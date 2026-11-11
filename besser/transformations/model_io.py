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
  W5  quantum_model_to_code() writes RXGate/RYGate/RZGate(..., angle=op.parameter) and fails with
      "'RXGate' object has no attribute 'parameter'": save_circuit() writes the circuit itself, with the
      gate constructors of the quantum metamodel.
  W6  The QiskitGenerator's template creates AerSimulator() without a seed, so counts change on every run:
      run_generated() runs the generated script unchanged while AerSimulator defaults seed_simulator to the
      seed of the Solver Configuration.
  W7  project_to_code() writes sets (links, association ends, set literals) in memory order, so one model gives
      a different file on every run: save_models() sorts what has no meaning in its order (_canonical).
  W8  class_buml_to_json() (the web editor's converter) gives every element a fresh uuid4, so one metamodel gives
      a different file on every run: save_metamodels() renumbers the ids in order of first appearance.
"""

import contextlib
import dataclasses
import functools
import io
import json
import re
import runpy
from pathlib import Path

from besser.BUML.metamodel import quantum
from besser.BUML.metamodel.object import ObjectModel
from besser.BUML.metamodel.project import Project
from besser.BUML.metamodel.structural import DomainModel, Metadata
from besser.utilities.buml_code_builder.project_builder import project_to_code
from besser.utilities.web_modeling_editor.backend.services.converters.buml_to_json.class_diagram_converter import (
    class_buml_to_json,
)
from bocl.OCLWrapper import OCLWrapper

ROOT = Path(__file__).resolve().parent.parent  # besser/, from where this file is (not the working directory)
PART_I = ROOT.parent / "metamodels" / "buml"  # Part I, at the repository root, read but never changed


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
def config_metamodel() -> DomainModel:
    """Solver Configuration DSL (config/solver_config_dsl.py)."""
    return load_buml(ROOT / "config" / "solver_config_dsl.py")["domain_model"]


@functools.cache
def problem_metamodel() -> DomainModel:
    """Problem DSL of Part I (Exam, Student, TimeSlot), read from ../metamodels/ and never changed."""
    return load_buml(PART_I / "problem_dsl.py")["domain_model"]


@functools.cache
def solution_metamodel() -> DomainModel:
    """Solution DSL of Part I (QUBO, Variable, LinearTerm, QuadraticTerm, Penalty), read from ../metamodels/."""
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


def check_ocl(domain_model: DomainModel, model: ObjectModel) -> list:
    """The OCL invariants of domain_model that model breaks, evaluated by BESSER's OCL interpreter (bocl).

    An invariant the interpreter cannot evaluate is reported as such rather than silently passed; the slides
    (T6, "BESSER pitfalls") note that forAll over objects, includes and isUnique are not supported.
    """
    wrapper = OCLWrapper(domain_model, model)
    failures = []
    for constraint in sorted(domain_model.constraints, key=lambda c: c.name):
        try:
            holds = wrapper.evaluate(constraint)
        except Exception as error:  # the interpreter's own limitations
            failures.append(f"{constraint.name}: not evaluated ({type(error).__name__})")
            continue
        if holds is not True:
            failures.append(f"{constraint.name}: {holds}")
    return failures


@dataclasses.dataclass
class Qubo:
    """A Solution DSL model read as numbers: f(x) = offset + sum linear[v] x_v + sum quadratic[{u, v}] x_u x_v."""
    offset: float
    variables: list  # labels, sorted by Variable.index (not necessarily 0..n-1: Part I's hand-made model skips some)
    linear: dict  # label -> coefficient
    quadratic: dict  # (label, label), in variables order -> coefficient
    penalties: dict  # Penalty.constraint -> list of the variable labels of its terms

    def energy(self, x: dict) -> float:
        """f(x) for an assignment label -> 0/1."""
        return (self.offset + sum(c * x[v] for v, c in self.linear.items())
                + sum(c * x[u] * x[v] for (u, v), c in self.quadratic.items()))


def read_qubo(model: ObjectModel) -> Qubo:
    """Read a model of Part I's Solution DSL (QUBO, Variable, LinearTerm, QuadraticTerm, Penalty)."""
    qubo = objects_of(model, "QUBO")[0]
    variables = [v.label for v in sorted(objects_of(model, "Variable"), key=lambda v: v.index)]
    position = {label: i for i, label in enumerate(variables)}
    linear, quadratic, penalties = {}, {}, {}
    for term in objects_of(model, "LinearTerm"):
        (v,) = linked(term, "variable")
        linear[v.label] = linear.get(v.label, 0.0) + term.coefficient
    for term in objects_of(model, "QuadraticTerm"):
        u, v = sorted((x.label for x in linked(term, "variable")), key=position.get)
        quadratic[(u, v)] = quadratic.get((u, v), 0.0) + term.coefficient
    for penalty in objects_of(model, "Penalty"):
        labels = {x.label for end in ("linearterm", "quadraticterm") for term in linked(penalty, end)
                  for x in linked(term, "variable")}
        penalties[penalty.constraint] = sorted(labels, key=position.get)
    return Qubo(qubo.offset, variables, linear, quadratic, penalties)


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
    path = stem.with_suffix(".py")
    path.write_text(_canonical(path.read_text(encoding="utf-8")), encoding="utf-8")  # W7
    stem.with_suffix(".json").write_text(json.dumps(to_json(model), indent=2) + "\n", encoding="utf-8")


_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


def save_metamodels(folder: Path) -> None:
    """Save each metamodel of the chain as <folder>/<name>.json, in the JSON of BESSER's web editor (the report
    draws its class diagrams from these files)."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for name, domain_model in [("problem_dsl", problem_metamodel()), ("solution_dsl", solution_metamodel()),
                               ("solver_config_dsl", config_metamodel())]:
        text = json.dumps(class_buml_to_json(domain_model), indent=1, ensure_ascii=False)
        ids = {}
        text = _UUID.sub(lambda m: ids.setdefault(m[0], str(len(ids))), text)  # W8
        (folder / f"{name}.json").write_text(text + "\n", encoding="utf-8")


_SET_OF_NAMES = re.compile(r"\{([A-Za-z_]\w*(?:, [A-Za-z_]\w*)+)\}")
_LINK_LINE = re.compile(r"^\w+_obj\.\w+ = ")
_BLOCK_START = re.compile(r"^\w+: (BinaryAssociation|Constraint) = ")
_CLASS_LINE = re.compile(r"^\w+ = Class\(")
_PROPERTY_LINE = re.compile(r"^\w+: Property = Property\(")
_ATTRIBUTES_HEADER = re.compile(r"^# \w+ class attributes and methods$")


def _canonical(code: str) -> str:
    """W7: the same file for the same model. Sorts what project_to_code writes in memory order: the items of set
    literals ({a_obj, b_obj}), the two ends of each association (ends={...}), the class definitions, the property
    definitions and the "attributes" block of each class, the association and constraint definitions, and the link
    assignments (x_obj.end = ...: each object end is assigned once, so their order does not matter)."""
    code = _SET_OF_NAMES.sub(lambda m: "{" + ", ".join(sorted(m.group(1).split(", "))) + "}", code)
    lines = _sort_ends(code.split("\n"))
    for single_line in (_CLASS_LINE, _PROPERTY_LINE, _LINK_LINE):
        lines = _sort_runs(lines, single_line.match, lambda i: i + 1)
    lines = _sort_runs(lines, _ATTRIBUTES_HEADER.match, lambda i: lines.index("", i) + 1)  # up to a blank line
    lines = _sort_runs(lines, _BLOCK_START.match, lambda i: i + _block_length(lines, i))
    return "\n".join(lines)


def _sort_ends(lines):
    result, i = [], 0
    while i < len(lines):
        if lines[i].strip() == "ends={":
            j = i + 1
            while lines[j].strip() != "}":
                j += 1
            ends = sorted(line.rstrip().rstrip(",") for line in lines[i + 1:j])
            result += [lines[i]] + [e + ("," if k < len(ends) - 1 else "") for k, e in enumerate(ends)] + [lines[j]]
            i = j + 1
        else:
            result.append(lines[i])
            i += 1
    return result


def _block_length(lines, i):
    j = i
    while lines[j] != ")":
        j += 1
    return j + 1 - i


def _sort_runs(lines, starts, end_of):
    """Sort each run of consecutive items; an item starts at a line where starts() holds and ends at end_of()."""
    result, i = [], 0
    while i < len(lines):
        if not starts(lines[i]):
            result.append(lines[i])
            i += 1
            continue
        items = []
        while i < len(lines) and starts(lines[i]):
            j = end_of(i)
            items.append(lines[i:j])
            i = j
        result += [line for item in sorted(items) for line in item]
    return result


def _operation(op) -> dict:
    """One operation of a QuantumCircuit as data (the gates T2 emits)."""
    supported = (quantum.HadamardGate, quantum.PauliXGate, quantum.RZGate, quantum.RXGate, quantum.Measurement)
    if not isinstance(op, supported):
        raise TypeError(f"save_circuit cannot write {type(op).__name__}")
    data = {"gate": type(op).__name__, "target": op.target_qubits[0]}
    if op.control_qubits:
        data["controls"] = list(op.control_qubits)
        data["control_states"] = [state.name for state in op.control_states]
    if isinstance(op, (quantum.RZGate, quantum.RXGate)):
        data["theta"] = op.theta
    if isinstance(op, quantum.Measurement):
        data["output_bit"] = op.output_bit
    return data


def circuit_to_json(circuit) -> dict:
    return {"name": circuit.name,
            "qregs": [{"name": r.name, "size": r.size} for r in circuit.qregs],
            "cregs": [{"name": r.name, "size": r.size} for r in circuit.cregs],
            "operations": [_operation(op) for op in circuit.operations]}


def save_circuit(stem: Path, circuit) -> None:
    """Save a QuantumCircuit as <stem>.py (B-UML quantum model, reloadable with load_buml: variable
    ``circuit``) and <stem>.json (W5: BESSER's own quantum_model_to_code fails on rotation gates)."""
    stem = Path(stem)
    stem.parent.mkdir(parents=True, exist_ok=True)
    data = circuit_to_json(circuit)
    lines = ["# Quantum model (BESSER quantum metamodel) of the chain's T2, written by",
             "# transformations/model_io.save_circuit (workaround W5). Generated: do not edit.",
             "from besser.BUML.metamodel.quantum import (",
             "    ClassicalRegister, ControlState, HadamardGate, Measurement, PauliXGate, QuantumCircuit,",
             "    QuantumRegister, RXGate, RZGate,",
             ")",
             "",
             f"circuit = QuantumCircuit(name={data['name']!r})"]
    lines += [f"circuit.add_qreg(QuantumRegister({r['name']!r}, {r['size']}))" for r in data["qregs"]]
    lines += [f"circuit.add_creg(ClassicalRegister({r['name']!r}, {r['size']}))" for r in data["cregs"]]
    for op in data["operations"]:
        if op["gate"] == "Measurement":
            args = f"target_qubit={op['target']}, output_bit={op['output_bit']}"
        else:
            args = f"target_qubit={op['target']}"
            if "theta" in op:
                args += f", theta={op['theta']!r}"
            if "controls" in op:
                states = ", ".join(f"ControlState.{state}" for state in op["control_states"])
                args += f", control_qubits={op['controls']}, control_states=[{states}]"
        lines.append(f"circuit.add_operation({op['gate']}({args}))")
    stem.with_suffix(".py").write_text("\n".join(lines) + "\n", encoding="utf-8")
    stem.with_suffix(".json").write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")


def run_generated(script: Path, seed: int, log: Path) -> dict:
    """Run a generated Qiskit script, unchanged, and return its counts (bit string -> shots); what it prints
    goes to log. W6: while it runs, AerSimulator() is seeded with the Solver Configuration's seed."""
    import qiskit_aer

    original = qiskit_aer.AerSimulator

    class SeededAerSimulator(original):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault("seed_simulator", seed)
            super().__init__(*args, **kwargs)

    printed = io.StringIO()
    qiskit_aer.AerSimulator = SeededAerSimulator
    try:
        with contextlib.redirect_stdout(printed):
            namespace = runpy.run_path(str(script), run_name="__main__")
    finally:
        qiskit_aer.AerSimulator = original
    Path(log).write_text(printed.getvalue(), encoding="utf-8")
    return dict(namespace["counts"])
