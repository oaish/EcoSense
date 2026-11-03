import math
from datetime import datetime
from typing import Dict, List, Sequence, Tuple, TypeVar

T = TypeVar("T")


def calculate_mae(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    """Calculate Mean Absolute Error (MAE) between true and predicted values.

    MAE = (1/N) * sum(|y_true - y_pred|)
    """
    if not y_true or not y_pred or len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must be non-empty sequences of equal length.")

    total_abs_err = sum(abs(t - p) for t, p in zip(y_true, y_pred))
    return round(total_abs_err / len(y_true), 4)


def calculate_rmse(y_true: Sequence[float], y_pred: Sequence[float]) -> float:
    """Calculate Root Mean Squared Error (RMSE) between true and predicted values.

    RMSE = sqrt((1/N) * sum((y_true - y_pred)^2))
    """
    if not y_true or not y_pred or len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must be non-empty sequences of equal length.")

    total_sq_err = sum((t - p) ** 2 for t, p in zip(y_true, y_pred))
    return round(math.sqrt(total_sq_err / len(y_true)), 4)


def chronological_train_test_split(
    series: Sequence[T],
    test_ratio: float = 0.2,
) -> Tuple[Sequence[T], Sequence[T]]:
    """Chronologically split time-series data into train and test partitions.

    Guarantees no temporal leakage (all train points strictly precede test points).

    Args:
        series: Sequence of chronological data items.
        test_ratio: Proportion of series to reserve for testing (e.g. 0.2 = 20%).

    Returns:
        Tuple[Sequence[T], Sequence[T]]: (train_set, test_set)
    """
    if not series:
        return [], []

    if test_ratio <= 0.0 or test_ratio >= 1.0:
        raise ValueError("test_ratio must be between 0.0 and 1.0 (exclusive).")

    n = len(series)
    test_size = max(1, int(n * test_ratio))
    train_size = n - test_size

    if train_size < 1:
        # Edge case for very small sequences: at least 1 item in train
        train_size = 1
        test_size = n - 1

    return series[:train_size], series[train_size:]


def evaluate_forecast_metrics(
    y_true: Sequence[float],
    y_pred: Sequence[float],
) -> Dict[str, float]:
    """Calculate standard forecast evaluation metrics."""
    if not y_true or not y_pred:
        return {"mae": 0.0, "rmse": 0.0, "count": 0}

    return {
        "mae": calculate_mae(y_true, y_pred),
        "rmse": calculate_rmse(y_true, y_pred),
        "count": len(y_true),
    }
