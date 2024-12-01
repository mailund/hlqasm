import math

from circuits import CIRCUIT, emit_circuit
from gates import QUBITS, Gate, OneBitGate, ThreeBitGate
from stdgates import CX, H, X


class Bar(ThreeBitGate):
    class Foo(OneBitGate):
        body = (H((0)),)

    body = (CX(0, 1), Foo(1), CX(1, 2))


def u1(theta: float) -> type[OneBitGate]:
    class U1(OneBitGate):
        def __init__(self, qubit: int):
            super().__init__(qubit, f"u1({theta})")

    return U1


circuit: CIRCUIT = [
    H((0)) | ("01", (1, 2)),
    X((1)),
    H((0)),
    CX(0, 1),
    H((0)).inv,
    u1(math.pi / 2)(0),
    Bar(0, 1, 2),
]
print(emit_circuit(circuit))
