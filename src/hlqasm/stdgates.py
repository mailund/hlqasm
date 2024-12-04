from .gates import QUBIT, Gate, ParameterizedGate


# Making it a little easier to get the right constructor type checking.
# This doesn't do anything beyond constraining the number of qubits a
# gate can take when constructed.
class OneBitGate(Gate):
    no_quibits = 1

    def __init__(self, qubit: QUBIT) -> None:
        super().__init__(qubit)


class TwoBitGate(Gate):
    no_quibits = 2

    def __init__(self, qubit1: QUBIT, qubit2: QUBIT) -> None:
        super().__init__(qubit1, qubit2)


class ThreeBitGate(Gate):
    no_quibits = 3

    def __init__(self, qubit1: QUBIT, qubit2: QUBIT, qubit3: QUBIT) -> None:
        super().__init__(qubit1, qubit2, qubit3)


class H(OneBitGate):
    pass


class X(OneBitGate):
    pass


class CX(TwoBitGate):
    pass


class u1(ParameterizedGate):
    formal_params = ("theta",)
