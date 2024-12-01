import itertools
from graphlib import TopologicalSorter
from typing import Iterable, Iterator, Protocol

from gates import Gate

CIRCUIT = list["Gate | CIRCUIT"]


def flatten_circuit(circuit: CIRCUIT) -> list[Gate]:
    return list(
        itertools.chain(
            *[flatten_circuit(g) if isinstance(g, list) else [g] for g in circuit]
        )
    )


def qubits_in_gates(gates: Iterable[Gate]) -> set[int]:
    return {qubit for gate in gates for qubit in gate.qubits}


def no_qubits(gates: Iterable[Gate]) -> int:
    return max(qubits_in_gates(gates)) + 1


class QubitScope(Protocol):
    def qasm_qubits(self, *qubit: int) -> str: ...


class GlobalQubitScope(QubitScope):
    def qasm_qubits(self, *qubit: int) -> str:
        if len(qubit) == 1:
            return f"reg[{qubit[0]}]"
        else:
            return ",".join(f"reg[{q}]" for q in qubit)


class LocalQubitScope(QubitScope):
    def qasm_qubits(self, *qubit: int) -> str:
        if len(qubit) == 1:
            return f"q{qubit[0]}"
        else:
            return ",".join(f"q{q}" for q in qubit)


def emit_qubits(gate: Gate, scope: QubitScope) -> str:
    return f"{scope.qasm_qubits(*gate.qubits)}"


def emit_gate(gate: Gate, scope: QubitScope) -> str:
    return f"{gate.opcode} {emit_qubits(gate, scope)};"


def emit_gates(gates: Iterable[Gate], scope: QubitScope) -> Iterator[str]:
    for gate in gates:
        yield emit_gate(gate, scope)


def emit_gate_type(gate_type: type[Gate]) -> str | None:
    if gate_type.body is None:
        return None

    qubits = no_qubits(gate_type.body)
    args = ", ".join(f"q{i}" for i in range(qubits))
    scope = LocalQubitScope()
    return "\n".join(
        [
            f"gate {gate_type.__name__.lower()} {args}",
            "{",
            *("    " + s for s in emit_gates(gate_type.body, scope)),
            "}",
        ]
    )


def extract_gate_types(gates: Iterable[Gate]) -> set[type[Gate]]:
    gate_types = {type(gate) for gate in gates}
    for gate_type in list(gate_types):
        gate_types |= gate_type.dependencies
    return gate_types


def emit_circuit(circuit: CIRCUIT) -> str:
    global_scope = GlobalQubitScope()
    gates = flatten_circuit(circuit)

    # Sort the gate types since qASM (or at least qiskit) requires
    # that we define a gate before we use it.
    deps = {
        gate_type: [dep for dep in gate_type.dependencies]
        for gate_type in extract_gate_types(gates)
    }
    gate_types = TopologicalSorter(deps).static_order()
    gate_defs = "\n".join(filter(None, map(emit_gate_type, gate_types)))

    return "\n".join(
        [
            "OPENQASM 3.0;",
            'include "stdgates.inc";',
            "",
            gate_defs,
            "",
            "qubit[3] reg;",
            "",
            "\n".join(emit_gates(gates, global_scope)),
        ]
    )
