from enum import Enum


class ApneaType(Enum):
    NormalBreathing = 0
    Obstructive = 1
    Hypopnea = 2
    Central = 3
