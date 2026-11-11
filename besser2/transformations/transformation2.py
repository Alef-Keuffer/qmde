"""Solve the QUBO produced by transformation 1."""

from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass
from numbers import Real
from typing import Any


_VARIABLE_LABEL = re.compile(r"^x_(\d+)_b(\d+)_(.+)$")
_EXACT_VARIABLE_LIMIT = 16
_MAX_REPORTED_SOLUTIONS = 20
_ENERGY_TOLERANCE = 1e-9


@dataclass(frozen=True)
class ScheduleCandidate:
    energy: float
    assignments: tuple[tuple[int, str, tuple[int, ...]], ...]
    violations: tuple[str, ...]

    @property
    def is_feasible(self) -> bool:
        return not self.violations


@dataclass(frozen=True)
class QuboSolution:
    best_energy: float
    candidates: tuple[ScheduleCandidate, ...]
    exact: bool
    optimal_solution_count: int
    feasible_solution_count: int
    variable_count: int


def _objects_of(model: Any, classifier_name: str) -> list[Any]:
    return [
        obj for obj in model.objects
        if obj.classifier.name == classifier_name
    ]


def _attribute_value(obj: Any, attribute_name: str) -> Any:
    for slot in obj.slots:
        if slot.attribute.name == attribute_name:
            return slot.value.value
    raise ValueError(
        f"Object {obj.name!r} has no value for required attribute {attribute_name!r}"
    )


def _finite_number(obj: Any, attribute_name: str) -> float:
    value = _attribute_value(obj, attribute_name)
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{obj.name!r} {attribute_name} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{obj.name!r} {attribute_name} must be finite")
    return number


def _prepare_qubo(
    qubo_model: Any,
) -> tuple[
    list[int],
    dict[int, tuple[int, int, str]],
    dict[int, float],
    dict[tuple[int, int], float],
    float,
    set[tuple[int, int]],
]:
    qubos = _objects_of(qubo_model, "QUBO")
    if len(qubos) != 1:
        raise ValueError(f"Expected exactly one QUBO object, found {len(qubos)}")
    qubo = qubos[0]

    variables = list(qubo.variable)
    if not variables:
        raise ValueError("The QUBO must contain at least one variable")

    indices: list[int] = []
    labels: dict[int, str] = {}
    assignment_info: dict[int, tuple[int, int, str]] = {}
    variable_by_id: dict[int, int] = {}
    for variable in variables:
        index = _attribute_value(variable, "index")
        if isinstance(index, bool) or not isinstance(index, int) or index < 0:
            raise ValueError(
                f"{variable.name!r} index must be a non-negative integer"
            )
        if index in labels:
            raise ValueError(f"Duplicate QUBO variable index: {index}")

        label = _attribute_value(variable, "label")
        match = _VARIABLE_LABEL.fullmatch(label) if isinstance(label, str) else None
        if match is None:
            raise ValueError(
                f"{variable.name!r} label must have the form "
                "'x_<exam index>_b<batch index>_<exam name>'"
            )
        exam_index, batch_index = int(match[1]), int(match[2])
        exam_name = match[3]
        if not exam_name:
            raise ValueError(f"{variable.name!r} must identify its exam")

        indices.append(index)
        labels[index] = label
        assignment_info[index] = (exam_index, batch_index, exam_name)
        variable_by_id[id(variable)] = index

    indices.sort()
    if len(set(labels.values())) != len(labels):
        raise ValueError("QUBO variable labels must be unique")

    linear: dict[int, float] = {}
    for variable in variables:
        index = variable_by_id[id(variable)]
        term = variable.linearterm
        if term is None or term.classifier.name != "LinearTerm":
            raise ValueError(f"Variable {variable.name!r} must have one LinearTerm")
        linear[index] = _finite_number(term, "coefficient")

    quadratic: dict[tuple[int, int], float] = {}
    conflict_pairs: set[tuple[int, int]] = set()
    for term in qubo.quadraticterm:
        if term.classifier.name != "QuadraticTerm":
            raise ValueError(f"{term.name!r} is not a QuadraticTerm")
        endpoints = list(term.variable)
        if len(endpoints) != 2 or endpoints[0] is endpoints[1]:
            raise ValueError(f"{term.name!r} must connect two distinct variables")
        try:
            first = variable_by_id[id(endpoints[0])]
            second = variable_by_id[id(endpoints[1])]
        except KeyError as error:
            raise ValueError(
                f"{term.name!r} references a variable outside the QUBO"
            ) from error

        pair = tuple(sorted((first, second)))
        quadratic[pair] = quadratic.get(pair, 0.0) + _finite_number(
            term, "coefficient"
        )
        if not math.isfinite(quadratic[pair]):
            raise ValueError(f"Combined coefficient for {pair!r} must be finite")
        if term.name.startswith("conflict_"):
            conflict_pairs.add(pair)

    offset = _finite_number(qubo, "offset")
    return indices, assignment_info, linear, quadratic, offset, conflict_pairs


def _candidate(
    mask: int,
    positions: dict[int, int],
    assignment_info: dict[int, tuple[int, int, str]],
    conflict_pairs: set[tuple[int, int]],
    energy: float,
) -> ScheduleCandidate:
    selected = {
        index
        for index, position in positions.items()
        if mask & (1 << position)
    }

    exams: dict[int, tuple[str, list[int]]] = {}
    for index, (exam_index, batch_index, exam_name) in assignment_info.items():
        if exam_index not in exams:
            exams[exam_index] = (exam_name, [])
        elif exams[exam_index][0] != exam_name:
            raise ValueError(
                f"Exam index {exam_index} has inconsistent names in QUBO labels"
            )
        if index in selected:
            exams[exam_index][1].append(batch_index)

    violations: list[str] = []
    assignments: list[tuple[int, str, tuple[int, ...]]] = []
    for exam_index, (exam_name, batches) in sorted(exams.items()):
        selected_batches = tuple(sorted(batches))
        assignments.append((exam_index, exam_name, selected_batches))
        if len(selected_batches) != 1:
            violations.append(
                f"{exam_name} is assigned to {len(selected_batches)} batches"
            )

    for first, second in sorted(conflict_pairs):
        if first in selected and second in selected:
            first_info = assignment_info[first]
            second_info = assignment_info[second]
            violations.append(
                f"{first_info[2]} and {second_info[2]} share batch "
                f"{first_info[1] + 1}"
            )

    return ScheduleCandidate(
        energy=energy,
        assignments=tuple(assignments),
        violations=tuple(violations),
    )


def _energy(
    mask: int,
    positions: dict[int, int],
    linear: dict[int, float],
    quadratic: dict[tuple[int, int], float],
    offset: float,
) -> float:
    result = offset
    for index, coefficient in linear.items():
        if mask & (1 << positions[index]):
            result += coefficient
    for (first, second), coefficient in quadratic.items():
        if mask & (1 << positions[first]) and mask & (1 << positions[second]):
            result += coefficient
    return result


def _solve_exact(
    indices: list[int],
    positions: dict[int, int],
    assignment_info: dict[int, tuple[int, int, str]],
    linear: dict[int, float],
    quadratic: dict[tuple[int, int], float],
    offset: float,
    conflict_pairs: set[tuple[int, int]],
) -> QuboSolution:
    best_energy = math.inf
    best_masks: list[int] = []
    best_count = 0
    feasible_count = 0
    variable_count = len(indices)

    for mask in range(1 << variable_count):
        energy = _energy(mask, positions, linear, quadratic, offset)
        if energy < best_energy and not math.isclose(
            energy, best_energy, rel_tol=_ENERGY_TOLERANCE, abs_tol=_ENERGY_TOLERANCE
        ):
            best_energy = energy
            best_masks = [mask]
            best_count = 1
            feasible_count = 0
        elif math.isclose(
            energy,
            best_energy,
            rel_tol=_ENERGY_TOLERANCE,
            abs_tol=_ENERGY_TOLERANCE,
        ):
            best_count += 1
            if len(best_masks) < _MAX_REPORTED_SOLUTIONS:
                best_masks.append(mask)
        else:
            continue

        candidate = _candidate(
            mask,
            positions,
            assignment_info,
            conflict_pairs,
            energy,
        )
        if candidate.is_feasible:
            feasible_count += 1

    candidates = tuple(
        _candidate(
            mask,
            positions,
            assignment_info,
            conflict_pairs,
            best_energy,
        )
        for mask in best_masks
    )
    return QuboSolution(
        best_energy=best_energy,
        candidates=candidates,
        exact=True,
        optimal_solution_count=best_count,
        feasible_solution_count=feasible_count,
        variable_count=variable_count,
    )


def _solve_annealing(
    indices: list[int],
    positions: dict[int, int],
    assignment_info: dict[int, tuple[int, int, str]],
    linear: dict[int, float],
    quadratic: dict[tuple[int, int], float],
    offset: float,
    conflict_pairs: set[tuple[int, int]],
    num_reads: int,
    sweeps: int,
    seed: int,
) -> QuboSolution:
    variable_count = len(indices)
    neighbors: list[list[tuple[int, float]]] = [
        [] for _ in range(variable_count)
    ]
    for (first, second), coefficient in quadratic.items():
        first_position = positions[first]
        second_position = positions[second]
        neighbors[first_position].append((second_position, coefficient))
        neighbors[second_position].append((first_position, coefficient))

    rng = random.Random(seed)
    max_coefficient = max(
        [abs(value) for value in linear.values()]
        + [abs(value) for value in quadratic.values()]
        + [1.0]
    )
    start_temperature = max_coefficient * 4
    end_temperature = max(start_temperature * 0.001, 1e-9)
    best_energy = math.inf
    best_masks: set[int] = set()

    for _ in range(num_reads):
        state = [rng.randrange(2) for _ in range(variable_count)]
        current_energy = _energy(
            sum(value << position for position, value in enumerate(state)),
            positions,
            linear,
            quadratic,
            offset,
        )
        run_best_energy = current_energy
        run_best_mask = sum(value << position for position, value in enumerate(state))

        for sweep in range(sweeps):
            fraction = sweep / max(sweeps - 1, 1)
            temperature = start_temperature * (
                end_temperature / start_temperature
            ) ** fraction
            order = list(range(variable_count))
            rng.shuffle(order)
            for position in order:
                index = indices[position]
                direction = 1 - 2 * state[position]
                delta = direction * (
                    linear[index]
                    + sum(
                        coefficient * state[neighbor]
                        for neighbor, coefficient in neighbors[position]
                    )
                )
                if delta <= 0 or rng.random() < math.exp(-delta / temperature):
                    state[position] = 1 - state[position]
                    current_energy += delta

                if current_energy < run_best_energy and not math.isclose(
                    current_energy,
                    run_best_energy,
                    rel_tol=_ENERGY_TOLERANCE,
                    abs_tol=_ENERGY_TOLERANCE,
                ):
                    run_best_energy = current_energy
                    run_best_mask = sum(
                        value << bit for bit, value in enumerate(state)
                    )

        exact_run_energy = _energy(
            run_best_mask, positions, linear, quadratic, offset
        )
        if exact_run_energy < best_energy and not math.isclose(
            exact_run_energy,
            best_energy,
            rel_tol=_ENERGY_TOLERANCE,
            abs_tol=_ENERGY_TOLERANCE,
        ):
            best_energy = exact_run_energy
            best_masks = {run_best_mask}
        elif math.isclose(
            exact_run_energy,
            best_energy,
            rel_tol=_ENERGY_TOLERANCE,
            abs_tol=_ENERGY_TOLERANCE,
        ):
            if len(best_masks) < _MAX_REPORTED_SOLUTIONS:
                best_masks.add(run_best_mask)

    candidates = tuple(
        _candidate(
            mask,
            positions,
            assignment_info,
            conflict_pairs,
            best_energy,
        )
        for mask in sorted(best_masks)
    )
    feasible_count = sum(candidate.is_feasible for candidate in candidates)
    return QuboSolution(
        best_energy=best_energy,
        candidates=candidates,
        exact=False,
        optimal_solution_count=len(best_masks),
        feasible_solution_count=feasible_count,
        variable_count=variable_count,
    )


def solve_qubo(
    qubo_model: Any,
    *,
    num_reads: int = 100,
    sweeps: int = 1000,
    seed: int = 0,
) -> QuboSolution:
    """Find minimum-energy assignments and decode them into exam schedules.

    Small QUBOs are solved exhaustively. Larger QUBOs use reproducible local
    simulated annealing and are reported as best-found, not proven optimal.
    """
    if isinstance(num_reads, bool) or not isinstance(num_reads, int) or num_reads < 1:
        raise ValueError("num_reads must be a positive integer")
    if isinstance(sweeps, bool) or not isinstance(sweeps, int) or sweeps < 1:
        raise ValueError("sweeps must be a positive integer")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")

    (
        indices,
        assignment_info,
        linear,
        quadratic,
        offset,
        conflict_pairs,
    ) = _prepare_qubo(qubo_model)
    positions = {index: position for position, index in enumerate(indices)}

    common_args = (
        indices,
        positions,
        assignment_info,
        linear,
        quadratic,
        offset,
        conflict_pairs,
    )
    if len(indices) <= _EXACT_VARIABLE_LIMIT:
        return _solve_exact(*common_args)
    return _solve_annealing(*common_args, num_reads, sweeps, seed)
