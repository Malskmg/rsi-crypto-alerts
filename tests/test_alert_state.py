import pytest

from src.alert_state import (
    AlertState,
    classify_rsi,
    load_states,
    save_states,
    should_alert,
)


@pytest.mark.parametrize(
    ("rsi", "expected"),
    [
        (0, AlertState.LOWER_ZONE),
        (39.9, AlertState.LOWER_ZONE),
        (40, AlertState.LOWER_ZONE),
        (40.1, AlertState.NEUTRAL),
        (59.9, AlertState.NEUTRAL),
        (60, AlertState.UPPER_ZONE),
        (100, AlertState.UPPER_ZONE),
    ],
)
def test_classify_rsi(rsi, expected):
    assert classify_rsi(rsi) == expected


@pytest.mark.parametrize(
    "value",
    [-1, 101, float("nan")],
)
def test_invalid_rsi(value):
    with pytest.raises(ValueError):
        classify_rsi(value)


def test_alert_sequence():
    values = [45, 39, 35, 46, 40, 62, 65, 50]
    expected = [False, True, False, False, True, True, False, False]

    previous = AlertState.NEUTRAL
    actual = []

    for value in values:
        current = classify_rsi(value)
        actual.append(should_alert(previous, current))
        previous = current

    assert actual == expected


def test_states_are_persistent(tmp_path):
    path = tmp_path / "data" / "alert_state.json"
    states = {
        "AAVEUSDT": AlertState.LOWER_ZONE,
        "HYPEUSDT": AlertState.UPPER_ZONE,
    }

    save_states(states, path)

    assert load_states(path) == states


def test_missing_state_file(tmp_path):
    path = tmp_path / "missing.json"

    assert load_states(path) == {}


def test_corrupted_state_is_not_silently_reset(tmp_path):
    path = tmp_path / "alert_state.json"
    path.write_text("invalid json", encoding="utf-8")

    with pytest.raises(ValueError):
        load_states(path)