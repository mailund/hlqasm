from .gates import OneBitGate, ParameterizedGate, TwoBitGate


class H(OneBitGate):
    pass


class X(OneBitGate):
    pass


class CX(TwoBitGate):
    pass


class u1(ParameterizedGate):
    formal_params = ("theta",)
