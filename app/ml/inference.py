# -*- coding: utf-8 -*-
import numpy as np
import os
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
            default_path = os.path.join(os.path.dirname(__file__), "weights.npz")
            if os.path.exists(default_path):
                weights_path = default_path

        if weights_path is not None:
            if not os.path.exists(weights_path):
                raise FileNotFoundError(f"Model weight file not found at: {weights_path}")
            try:
                arrays = np.load(weights_path)
                w1 = arrays["w1"]
                b1 = arrays["b1"]
                w2 = arrays["w2"]  
                b2 = arrays["b2"]  
            except Exception as e:
                raise FileNotFoundError(f"Model weight file corrupted: {str(e)}")
        else:
            np.random.seed(42)
            w1 = np.random.randn(4, 32) * np.sqrt(2.0 / 4)
            b1 = np.zeros(32)
            w2 = np.random.randn(32, 3) * np.sqrt(2.0 / 32)  
            b2 = np.zeros(3)                                 

        self.layer1 = Linear(4, 32, w1, b1)
        self.layer2 = Linear(32, 3, w2, b2)

    def predict_probabilities(self, x_input: np.ndarray) -> np.ndarray:
        t_in = Tensor(x_input)
        x = self.layer1.forward(t_in)
        x = x.relu()
        logits = self.layer2.forward(x)
        
        logits_data = logits.data.reshape(-1)
        exp_logits = np.exp(logits_data - np.max(logits_data))
        softmax_probs = exp_logits / np.sum(exp_logits)
        
        return softmax_probs

