from ..root import rootclass
from ..root import whatever

class subclass(rootclass):
    def __init__(self) -> None:
        super().__init__()
        whatever()
        print("sub class init")