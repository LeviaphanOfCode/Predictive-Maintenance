import numpy as np
from app.core.config import settings

class Tensor:
    def __init__(self, data):
        self.data = np.array(data)

    def mm(self, x):
        return Tensor(self.data @ x.data)

    def __add__(self, other):
        return Tensor(self.data + other.data)

    def relu(self):
        return Tensor((self.data > 0) * self.data)

class Linear:
    def __init__(self, n_inputs, n_outputs, weights=None, bias=None):
        if weights is not None:
            self.weight = Tensor(weights)
            self.bias = Tensor(bias)
        else:
            W = np.random.randn(n_inputs, n_outputs) * np.sqrt(2.0 / n_inputs)
            self.weight = Tensor(W)
            self.bias = Tensor(np.zeros(n_outputs))

    def forward(self, input_tensor):
        return input_tensor.mm(self.weight) + self.bias

class InferenceEngine:
    def __init__(self, weights_path=None):
        self.model_version = settings.MODEL_VERSION
        
        if weights_path is None:
            np.random.seed(42)
            w1 = np.random.randn(7, 32) * np.sqrt(2.0 / 7)
            b1 = np.zeros(32)
            w2 = np.random.randn(32, 1) * np.sqrt(2.0 / 32)
            b2 = np.zeros(1)
        else:
            raise FileNotFoundError("Model weight file corrupted or missing")

        self.layer1 = Linear(7, 32, w1, b1)
        self.layer2 = Linear(32, 1, w2, b2)

    def predict_probabilities(self, x_input: np.ndarray) -> float:
        t_in = Tensor(x_input)
        x = self.layer1.forward(t_in)
        x = x.relu()
        logits = self.layer2.forward(x)
        prob = 1.0 / (1.0 + np.exp(-logits.data))
        return float(prob.item())

