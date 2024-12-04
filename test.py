import math

from hlqasm.gates import OneBitGate, ThreeBitGate
from hlqasm.stdgates import CX, H, X, u1


class Bar(ThreeBitGate):
    class Foo(OneBitGate):
        body = (H((0)),)

    body = (CX(0, 1), Foo(1), CX(1, 2))


circuit = [
    H((0)) | ("01", (1, 2)),
    X((1)),
    H((0)),
    CX(0, 1),
    H((0)).inv,
    u1(math.pi / 2)(0),
    Bar(0, 1, 2),
]
