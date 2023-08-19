from typing import List

class ICCProfile:
    buffer: int
    data_color_space: int
    has_A2B: bool
    has_toXYZD50: bool
    has_trc: bool
    pcs: int
    size: int
    tag_count: int
    def __init__(self) -> None: ...

class Matrix3x3:
    def __init__(self, v: List[float]) -> None: ...

class TransferFunction:
    def __init__(self, v: List[float]) -> None: ...
