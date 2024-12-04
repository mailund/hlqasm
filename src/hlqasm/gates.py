from __future__ import annotations

import copy
from typing import Any, ClassVar, Iterable, Self

QUBIT = int
QUBITS = tuple[QUBIT, ...]


class GateType(type):
    # Keeping track of gate definitions and their dependencies
    name: str
    body: Iterable[Gate] | None = None
    dependencies: set[type[Gate]] = set()
    no_qubits: int | None

    def __init__(
        cls,
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, object],
        no_qubit: int | None = None,
    ) -> None:

        super().__init__(name, bases, attrs)

        cls.name = name.lower()

        no_qubits = no_qubit or attrs.get("no_qubits", None)
        if no_qubits is not None and not isinstance(no_qubits, int):
            raise ValueError(f"Expected an integer for no_qubits, got {no_qubits}")

        # Collect all gate definitions to configure this class's dependencies
        if cls.body is not None:
            cls.dependencies = {
                type(gate) for gate in cls.body if type(gate).body is not None
            }
            for gate_type in cls.dependencies:
                cls.dependencies.update(gate_type.dependencies)

            if no_qubits is None:
                no_qubits = max(max(gate.qubits) for gate in cls.body) + 1

        cls.no_qubits = no_qubits


class Gate(metaclass=GateType):
    """
    A gate in the circuit.
    """

    opcode: str
    qubits: QUBITS

    @property
    def name(self) -> str:
        """The name of the gate."""
        return self.__class__.__name__.lower()

    def __init__(self, *qubits: QUBIT, opcode: str | None = None) -> None:
        self.opcode = opcode or self.__class__.__name__.lower()
        self.qubits = qubits

        if type(self).no_qubits is not None and len(qubits) != type(self).no_qubits:
            raise ValueError(
                f"Expected {type(self).no_qubits} qubits, got {len(qubits)}: {qubits}"
            )

    def __repr__(self) -> str:
        return f"Gate(*{self.qubits!r}, opcode={self.opcode!r})"

    @property
    def inv(self) -> Gate:
        """Getting the inverse of this gate."""
        return Gate(*self.qubits, opcode=f"inv @ {self.opcode}")

    def control(self, control_str: str, ctrl_qubits: QUBITS) -> Gate:
        """Transform this gate into a controlled gate."""
        control_str = control_str or "".join(str(int(a >= 0)) for a in ctrl_qubits)
        ctrl_qubits = tuple(~a if a < 0 else a for a in ctrl_qubits)
        ctrl_opcode = " @ ".join("ctrl" if c == "1" else "negctrl" for c in control_str)
        opcode = f"{ctrl_opcode} @ {self.opcode}"
        return Gate(*ctrl_qubits, *self.qubits, opcode=opcode)

    def __or__(self, ctrl: tuple[str, QUBITS] | QUBITS | int) -> Gate:
        """Syntactic sugar for controlling the gate."""
        match ctrl:
            case int(bit):
                return self.control("", (bit,))
            case (str(ctrl_str), tuple(ctrl_bits)):
                return self.control(ctrl_str, ctrl_bits)
            case tuple(bits):
                return self.control("", bits)

    def __replace__(self, /, **changes: Any) -> Self:
        cpy = copy.copy(self)
        for key, value in changes.items():
            if key not in self.__dict__:
                raise ValueError(f"Unknown attribute {key}")
            setattr(cpy, key, value)
        return cpy

    def relocate(self, qubit_map: dict[QUBIT, QUBIT]) -> Self:
        """Relocate the gate to new qubits."""
        try:
            qubits = tuple(qubit_map[q] for q in self.qubits)
            return copy.replace(self, qubits=qubits)
        except KeyError as e:
            raise KeyError(f"Error mapping {self.qubits} through {qubit_map}") from e


class ParameterizedGate(GateType):
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

    def __new__(cls, *_ignored: float) -> ParameterizedGate:
        """
        Create a new parameterised gate.

        Creating a new parameterised gate means making a new class
        (because we model gate types as meta-classes) so we need to map the __new__
        arguments to those expected for classes).
        """
        return super().__new__(cls, "ParameterizedGate", (ParameterizedGate,), {})

    def __init__(self, *args: float) -> None:
        if len(args) != len(self.formal_params):
            raise ValueError(
                f"Expected {len(self.formal_params)} parameters, got {len(args)}"
            )

        self.opcode = f"{self.gate_name}({', '.join(f'{a}' for a in args)})"

    def __call__(self, *qubits: QUBIT) -> Gate:
        return Gate(*qubits, opcode=self.opcode)
