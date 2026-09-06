import numpy as np
from numpy.typing import NDArray

class Tensor:
    def unsqueeze(self, dim: int) -> Tensor: ...

def from_numpy(array: NDArray[np.float32]) -> Tensor: ...
