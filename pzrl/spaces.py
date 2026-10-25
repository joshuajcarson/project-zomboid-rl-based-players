"""Tiny stand-ins for gymnasium spaces so the env works without gymnasium; real gymnasium spaces are used when installed."""
import numpy as np

try:  # pragma: no cover - optional dependency
    from gymnasium.spaces import Box, Discrete
except Exception:
    class Discrete:
        def __init__(self, n):
            self.n = int(n)
            self.shape = ()
            self.dtype = np.int64

        def sample(self):
            return int(np.random.randint(self.n))

        def contains(self, x):
            return 0 <= int(x) < self.n

    class Box:
        def __init__(self, low, high, shape, dtype=np.float32):
            self.low, self.high, self.shape, self.dtype = low, high, tuple(shape), dtype

        def sample(self):
            return np.random.uniform(self.low, self.high, self.shape).astype(self.dtype)

        def contains(self, x):
            x = np.asarray(x)
            return x.shape == self.shape and bool(np.all(x >= self.low) and np.all(x <= self.high))
