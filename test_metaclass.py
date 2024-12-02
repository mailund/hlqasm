from __future__ import annotations

from typing import Any, ClassVar
from typing import Literal as L
from typing import overload

QUBIT = int
QUBITS = tuple[QUBIT, ...]


class GateType[N](type):
    opcode: str

    def __new__(
        cls, name: str, bases: tuple[type, ...], namespace: dict[str, object]
    ) -> Any:
        namespace["opcode"] = name.lower()
        return super().__new__(cls, name, bases, namespace)

    # All gates must be creatable from the right number of qubits...
    @overload
    def __call__(cls: GateType[L[0]]) -> Gate: ...
    @overload
    def __call__(cls: GateType[L[1]], q: QUBIT, /) -> Gate: ...
    @overload
    def __call__(cls: GateType[L[2]], q1: QUBIT, q2: QUBIT, /) -> Gate: ...
    @overload
    def __call__(cls, *qubits: QUBIT) -> Gate: ...

    def __call__(cls, *qubits: QUBIT) -> Gate:
        return super().__call__(*qubits)


class Gate(metaclass=GateType[Any]):
    qubits: QUBITS

    def __init__(self, *qubits: QUBIT) -> None:
        self.qubits = qubits

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.qubits})"

    @property
    def inv(self) -> Gate:
        return InverseGateType(self)()

    def control(self, control_str: str, ctrl_qubits: QUBITS) -> Gate:
        control_str = control_str or "".join(str(int(a >= 0)) for a in ctrl_qubits)
        control_bits = tuple(~a if a < 0 else a for a in ctrl_qubits)
        return ControlledGateType(self, control_str)(*control_bits)

    def __or__(self, ctrl: tuple[str, QUBITS] | QUBITS | int) -> Gate:
        """Syntactic sugar for controlling the gate."""
        match ctrl:
            case int(bit):
                return self.control("", (bit,))
            case (str(ctrl_str), tuple(ctrl_bits)):
                return self.control(ctrl_str, ctrl_bits)
            case tuple(bits):
                return self.control("", bits)

    # Keeping track of gate definitions and their dependencies
    body: ClassVar[tuple[Gate, ...] | None] = None
    dependencies: ClassVar[set[type[Gate]]] = set()

    def __init_subclass__(cls) -> None:
        # Collect all gate definitions
        if cls.body is not None:
            cls.dependencies = {
                type(gate) for gate in cls.body if type(gate).body is not None
            }
            for gate_type in cls.dependencies:
                cls.dependencies.update(gate_type.dependencies)

        return super().__init_subclass__()


class InverseGateType(GateType[L[0]]):
    def __new__(cls, underlying: Gate) -> InverseGateType:
        name = f"{underlying.__class__.__name__}†"
        bases = (Gate,)
        namespace: dict[str, object] = {"underlying": underlying}
        return super().__new__(cls, name, bases, namespace)

    def __init__(cls, underlying: Gate) -> None:
        cls.underlying = underlying
        cls.opcode = f"inv @ {underlying.opcode}"


class ControlledGateType[N](GateType[N]):
    def __new__(cls, underlying: Gate, ctrl: str) -> ControlledGateType[N]:
        name = f"[{underlying.__class__.__name__} | {ctrl}]"
        bases = (Gate,)
        namespace: dict[str, object] = {"underlying": underlying, "ctrl": ctrl}
        return super().__new__(cls, name, bases, namespace)

    def __init__(cls, underlying: Gate, ctrl: str) -> None:
        cls.underlying = underlying
        ctrl_opcode = " @ ".join("ctrl" if c == "1" else "negctrl" for c in ctrl)
        cls.opcode = f"{ctrl_opcode} @ {underlying.opcode}"

    def __call__(cls, *control_bits: QUBIT) -> Gate:
        return super().__call__(*control_bits, *cls.underlying.qubits)


class H(Gate):
    def __init__(self, qubit: QUBIT) -> None:
        super().__init__(qubit)


class X(Gate):
    def __init__(self, qubit: QUBIT) -> None:
        super().__init__(qubit)


class CX(Gate):
    def __init__(self, control: QUBIT, target: QUBIT) -> None:
        super().__init__(control, target)


circuit: list[Gate] = [
    H(0) | ("01", (1, 2)),
    X(1),
    H(0),
    CX(0, 1),
    H(0).inv,
    # u1(math.pi / 2)(0),
    # Bar(0, 1, 2),
]
print(circuit)
print()
for gate in circuit:
    print(gate.opcode, gate.qubits)
