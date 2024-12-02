from gates import OneBitGate, ParameterizedGate, TwoBitGate


class H(OneBitGate):
    pass


class X(OneBitGate):
    pass


class CX(TwoBitGate):
    pass


class u1(ParameterizedGate):
    formal_params = ("theta",)


u1(0.0)()
u1(0.0)(0)
u1(0.0)(0, 1)
u1(0.0)(0, 1, 2)
