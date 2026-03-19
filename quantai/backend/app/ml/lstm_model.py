# backend/app/ml/lstm_model.py
from __future__ import annotations

import numpy as np

try:
    import torch
    import torch.nn as nn
except Exception:  # pragma: no cover
    torch = None
    nn = None


if torch is not None:
    class PriceActionLSTM(nn.Module):
        def __init__(self, input_size: int = 16, hidden_size: int = 128, num_layers: int = 2, dropout: float = 0.2) -> None:
            super().__init__()
            self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size, num_layers=num_layers, dropout=dropout, batch_first=True)
            self.attn = nn.MultiheadAttention(embed_dim=hidden_size, num_heads=4, batch_first=True)
            self.head = nn.Sequential(nn.Linear(hidden_size, 1), nn.Sigmoid())

        def forward(self, x):
            out, _ = self.lstm(x)
            attn_out, weights = self.attn(out, out, out)
            self._last_weights = weights
            return self.head(attn_out[:, -1, :])

        def predict_proba(self, x) -> float:
            with torch.no_grad():
                y = self.forward(x)
            return float(y.squeeze().item())

        def get_attention_weights(self, x) -> np.ndarray:
            _ = self.forward(x)
            return self._last_weights.detach().cpu().numpy()
else:
    class PriceActionLSTM:
        def __init__(self, *args, **kwargs) -> None:
            _ = args, kwargs

        def forward(self, x):
            _ = x
            return 0.5

        def predict_proba(self, x) -> float:
            _ = x
            return 0.5

        def get_attention_weights(self, x) -> np.ndarray:
            _ = x
            return np.array([[0.5]])
