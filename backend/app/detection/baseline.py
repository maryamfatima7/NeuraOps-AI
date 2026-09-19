import math
from collections import deque
from datetime import datetime


class BaselineDetector:
    def __init__(self, window_size: int = 12):
        self.window_size = window_size
        self.history = {}

    def update(self, service: str, metric: str, value: float):
        key = (service, metric)
        data = self.history.setdefault(key, deque(maxlen=self.window_size))
        data.append(value)

    def analyze(self, service: str, metric: str, value: float):
        history = self.history.get((service, metric), deque(maxlen=self.window_size))
        if len(history) < 3:
            return None

        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        std_dev = math.sqrt(variance)
        if std_dev == 0:
            return None

        z_score = abs((value - mean) / std_dev)
        deviation = abs(value - mean)
        threshold = 2.5
        if z_score > threshold or deviation > mean * 0.3:
            severity = "HIGH" if z_score > 4 or deviation > mean * 0.7 else "MEDIUM"
            return {
                "metric": metric,
                "service": service,
                "observed_value": value,
                "expected_baseline": round(mean, 4),
                "deviation": round(deviation, 4),
                "severity": severity,
                "explanation": f"Value deviated from rolling baseline by {z_score:.2f} standard deviations.",
                "timestamp": datetime.utcnow(),
            }
        return None
