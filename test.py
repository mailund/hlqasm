from circuits import CIRCUIT, emit_circuit
from gates import OneBitGate, ThreeBitGate
from stdgates import CX, H, X


class Foo(OneBitGate):
    body = (H((0)),)


class Bar(ThreeBitGate):
    body = (CX(0, 1), Foo(1), CX(1, 2))


circuit: CIRCUIT = [
    H((0)) | ("01", (1, 2)),
    X((1)),
    H((0)),
    CX(0, 1),
    H((0)).inv,
    Bar(0, 1, 2),
]
print(emit_circuit(circuit))
