from typing import Self


class QReg:
    def __init__(
        self, size: int | None = None, name: str = "", wires: tuple[int, ...] = ()
    ) -> None:
        self.name = name
        self.size = size or len(wires)
        self.wires = wires or (tuple(range(size)) if size else ())

    def set_name(self, name: str) -> Self:
        self.name = name
        return self

    def set_wires(self, wires: tuple[int, ...]) -> Self:
        self.wires = wires
        return self

    def __getitem__(self, index: int) -> int:
        return self.wires[index]

    def __str__(self) -> str:
        return f"{self.name}[{self.size}]"

    def __repr__(self) -> str:
        return str(self)
