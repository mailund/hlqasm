from __future__ import annotations

from typing import ClassVar

QUBIT = int
QUBITS = tuple[QUBIT, ...]


class Gate:
    opcode: str
    qubits: QUBITS

    def __init__(self, qubits: QUBITS) -> None:
        self.opcode = self.__class__.__name__.lower()
        self.qubits = qubits

    @property
    def inv(self) -> Gate:
        return InverseGate(self)

    def control(self, control_str: str, ctrl_qubits: QUBITS) -> Gate:
        control_str = control_str or "".join(str(int(a >= 0)) for a in ctrl_qubits)
        control_bits = tuple(~a if a < 0 else a for a in ctrl_qubits)
        return ControlledGate(self, control_str, control_bits)

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


class ControlledGate(Gate):
    def __init__(self, underlying: Gate, ctrl_str: str, ctrl_qubits: QUBITS) -> None:
        super().__init__(underlying.qubits + ctrl_qubits)
        ctrl_opcode = " @ ".join("ctrl" if c == "1" else "negctrl" for c in ctrl_str)
        self.opcode = f"{ctrl_opcode} @ {underlying.opcode}"


class InverseGate(Gate):
    def __init__(self, underlying: Gate) -> None:
        super().__init__(underlying.qubits)
        self.opcode = f"inv @ {underlying.opcode}"


# Making it a little easier to get the right constructors
class OneBitGate(Gate):
    def __init__(self, qubit: QUBIT) -> None:
        super().__init__((qubit,))


class TwoBitGate(Gate):
    def __init__(self, qubit1: QUBIT, qubit2: QUBIT) -> None:
        super().__init__((qubit1, qubit2))


class ThreeBitGate(Gate):
    def __init__(self, qubit1: QUBIT, qubit2: QUBIT, qubit3: QUBIT) -> None:
        super().__init__((qubit1, qubit2, qubit3))
