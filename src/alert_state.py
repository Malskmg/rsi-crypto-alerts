import json
from enum import Enum
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = PROJECT_ROOT / "data" / "alert_state.json"


class AlertState(str, Enum):
    NEUTRAL = "neutral"
    LOWER_ZONE = "lower_zone"
    UPPER_ZONE = "upper_zone"


def classify_rsi(
    value: float,
    lower: float = 40,
    upper: float = 60,
) -> AlertState:
    if lower >= upper:
        raise ValueError("Le seuil bas doit être inférieur au seuil haut.")

    if not 0 <= value <= 100:
        raise ValueError("Le RSI doit être compris entre 0 et 100.")

    if value <= lower:
        return AlertState.LOWER_ZONE

    if value >= upper:
        return AlertState.UPPER_ZONE

    return AlertState.NEUTRAL


def should_alert(
    previous: AlertState,
    current: AlertState,
) -> bool:
    return current != AlertState.NEUTRAL and current != previous


def load_states(path: Path = STATE_FILE) -> dict[str, AlertState]:
    if not path.exists():
        return {}

    raw = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(raw, dict):
        raise ValueError("Le fichier d'état doit contenir un objet JSON.")

    return {
        symbol: AlertState(value)
        for symbol, value in raw.items()
    }


def save_states(
    states: dict[str, AlertState],
    path: Path = STATE_FILE,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        symbol: state.value
        for symbol, state in states.items()
    }

    temporary_path = path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    temporary_path.replace(path)