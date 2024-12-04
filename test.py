import math

from hlqasm import Circuit, QReg
from hlqasm.pauli import pauli_circuit, pauli_gate
from hlqasm.stdgates import CX, H, OneBitGate, ThreeBitGate, Toffoli, X, u1


# Defining new gates... the `body` attribute is a list of gates that make up the new gate
class Bar(ThreeBitGate):
    class Foo(OneBitGate):
        body = (H((0)),)

    body = (CX(0, 1), Foo(1), CX(1, 2))


# Defining new circuits. The body again is a list of gates that make up the circuit,
# but the class is translated into a callable where you can provide the registers
class Program(Circuit):
    qreg = QReg(2)
    body = [
        H(qreg[0]),
        X(qreg[1]),
        CX(qreg[0], qreg[1]),
    ]

    a, b = QReg(2), QReg(2)
    body += [
        CX(a[0], b[0]),
        CX(a[1], b[1]),
    ]


# Anything you leave in `circuit` is the program
circuit = [
    H((0)) | ("01", (1, 2)),
    X((1)),
    H((0)),
    CX(0, 1),
    H((0)).inv,
    u1(math.pi / 2)(0),
    Bar(0, 1, 2),
    Toffoli(0, 1, 5),
    X(5) | (0, 1),
]


qreg = QReg(4)
a = QReg(wires=(4, 5, 6))
b = QReg(wires=(7, 8, 9))
Program(qreg=qreg, a=a, b=b)  # Calling the Program circuit with a register mapping

circuit += Program(qreg=qreg, a=a, b=b)

Pxx = pauli_circuit("XX")
circuit += Pxx(target_reg=a)
circuit += [pauli_gate("YZY")(0, 1, 2)]
