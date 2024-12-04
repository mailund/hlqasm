from typing import Any, ClassVar

from .emit import GateStream
from .gates import Gate
from .qreg import QReg


class AsmScopeDict(dict[str, object]):
    wires_used: int

    def __init__(self) -> None:
        self.wires_used = 0
        super().__init__()

    def __setitem__(self, name: str, value: Any) -> None:
        if isinstance(value, QReg):
            value.set_name(name)
            wires_used = self.wires_used
            self.wires_used += value.size
            value.set_wires(tuple(range(wires_used, self.wires_used)))
        super().__setitem__(name, value)


class AsmScopeMeta(type):
    __body__: list[Gate]
    __registers__: ClassVar[dict[str, QReg]] = {}

    @classmethod
    def __prepare__(
        metacls, name: str, bases: tuple[type, ...], /, **kwds: Any
    ) -> dict[str, object]:
        super().__prepare__(name, bases, **kwds)
        return AsmScopeDict()

    def __new__(
        cls, name: str, bases: tuple[type, ...], attrs: dict[str, object]
    ) -> type:
        attrs["__body__"] = attrs.get("body", [])
        attrs["__registers__"] = {
            name: value for name, value in attrs.items() if isinstance(value, QReg)
        }
        return super().__new__(cls, name, bases, attrs)

    def __call__(cls, **regs: QReg) -> GateStream:
        assert len(regs) == len(cls.__registers__)
        for name, reg in regs.items():
            assert name in cls.__registers__
            assert cls.__registers__[name].size <= reg.size

        wire_map: dict[int, int] = {}
        for name, reg in regs.items():
            mapped = cls.__registers__[name]
            wire_map |= dict(zip(mapped.wires, reg.wires))

        return [gate.relocate(wire_map) for gate in cls.__body__]


class Circuit(metaclass=AsmScopeMeta):
    pass
