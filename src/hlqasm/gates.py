from __future__ import annotations

from typing import ClassVar

QUBIT = int
QUBITS = tuple[QUBIT, ...]


class Gate:
    opcode: str
    qubits: QUBITS

    def __init__(self, *qubits: QUBIT, opcode: str | None = None) -> None:
        self.opcode = opcode or self.__class__.__name__.lower()
        self.qubits = qubits

    def __repr__(self) -> str:
        return f"Gate(*{self.qubits!r}, opcode={self.opcode!r})"

    @property
    def inv(self) -> Gate:
        return Gate(*self.qubits, opcode=f"inv @ {self.opcode}")

    def control(self, control_str: str, ctrl_qubits: QUBITS) -> Gate:
        control_str = control_str or "".join(str(int(a >= 0)) for a in ctrl_qubits)
        ctrl_qubits = tuple(~a if a < 0 else a for a in ctrl_qubits)
        ctrl_opcode = " @ ".join("ctrl" if c == "1" else "negctrl" for c in control_str)
        opcode = f"{ctrl_opcode} @ {self.opcode}"
        return Gate(*self.qubits, *ctrl_qubits, opcode=opcode)

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


class ParameterizedGate:
    """
    A type that gives you a gate generator when provided with parameters.

    This is mostly intended as a wrapper around qASM parameterised gates. For home-brewed
    gates, just use Python functions. They are more expressive and easier to use.
    """

    gate_name: ClassVar[str]
    formal_params: ClassVar[tuple[str, ...]]

    def __init_subclass__(cls) -> None:
        cls.gate_name = getattr(cls, "gate_name", cls.__name__.lower())
        cls.formal_params = getattr(cls, "formal_params", ())

    def __init__(self, *args: float) -> None:
        assert len(args) == len(self.formal_params)
        self.opcode = f"{self.gate_name}({', '.join(f'{a}' for a in args)})"

    def __call__(self, *qubits: QUBIT) -> Gate:
        return Gate(*qubits, opcode=self.opcode)


# Making it a little easier to get the right constructor type checking.
# This doesn't do anything beyond constraining the number of qubits a
# gate can take when constructed.
class OneBitGate(Gate):
    def __init__(self, qubit: QUBIT) -> None:
        super().__init__(qubit)


class TwoBitGate(Gate):
    def __init__(self, qubit1: QUBIT, qubit2: QUBIT) -> None:
        super().__init__(qubit1, qubit2)


class ThreeBitGate(Gate):
    def __init__(self, qubit1: QUBIT, qubit2: QUBIT, qubit3: QUBIT) -> None:
        super().__init__(qubit1, qubit2, qubit3)
