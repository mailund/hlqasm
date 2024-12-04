from typing import ClassVar, Self

from gates import Gate
from stdgates import CX, H, X


class Register:
    def __init__(self, size: int, name: str = "") -> None:
        self.size = size
        self.name = name

    def set_name(self, name: str) -> Self:
        self.name = name
        return self

    def __getitem__(self, index: int) -> int:
        return 0  # FIXME

    def __str__(self) -> str:
        return f"{self.name}[{self.size}]"

    def __repr__(self) -> str:
        return str(self)


class AsmScopeMeta(type):
    __body__: list[Gate]
    __registers__: ClassVar[dict[str, Register]] = {}

    def __new__(
        cls, name: str, bases: tuple[type, ...], attrs: dict[str, object]
    ) -> type:
        attrs["__body__"] = attrs.get("body", [])
        attrs["__registers__"] = {
            name: value.set_name(name)
            for name, value in attrs.items()
            if isinstance(value, Register)
        }
        return super().__new__(cls, name, bases, attrs)


class AsmScope(metaclass=AsmScopeMeta):
    pass


class Program(AsmScope):
    qreg = Register(4)
    a, b = Register(2), Register(2)
    body = [
        H(qreg[0]),
        X(qreg[1]),
        CX(qreg[0], qreg[1]),
    ]


print(Program.__body__, Program.__registers__)
