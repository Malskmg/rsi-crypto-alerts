import argparse
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from src.alert_state import (
    AlertState,
    classify_rsi,
    load_states,
    save_states,
    should_alert,
)
from src.binance_data import get_klines
from src.config import (
    CONTEXT_INTERVAL,
    PARIS_TIMEZONE,
    RSI_LOWER_LIMIT,
    RSI_PERIOD,
    RSI_UPPER_LIMIT,
    SYMBOLS,
    TRIGGER_INTERVAL,
)
from src.indicators import compute_rsi
from src.telegram_alerts import send_telegram_message


def format_pair(symbol: str) -> str:
    if symbol.endswith("USDT"):
        return f"{symbol[:-4]}/USDT"

    return symbol


def build_message(
    symbol: str,
    rsi_15m: float,
    rsi_4h: float,
    state: AlertState,
    observed_at: datetime,
) -> str:
    if state == AlertState.LOWER_ZONE:
        zone = "Zone basse"
        condition = f"RSI 15 min <= {RSI_LOWER_LIMIT}"
    else:
        zone = "Zone haute"
        condition = f"RSI 15 min >= {RSI_UPPER_LIMIT}"

    timestamp = observed_at.strftime(
        "%d/%m/%Y %H:%M:%S %Z (UTC%z)"
    )

    return (
        f"ALERTE RSI — {format_pair(symbol)}\n\n"
        f"Heure de vérification : {timestamp}\n"
        f"Fuseau : Paris\n\n"
        f"RSI({RSI_PERIOD}) 15 min : {rsi_15m:.2f}\n"
        f"RSI({RSI_PERIOD}) 4 h : {rsi_4h:.2f}\n\n"
        f"Condition : {condition}\n"
        f"État : {zone}\n\n"
        "Valeurs calculées avec les bougies en cours."
    )


def check_symbol(
    symbol: str,
    states: dict[str, AlertState],
    dry_run: bool,
) -> None:
    df_15m = get_klines(symbol, TRIGGER_INTERVAL)
    df_4h = get_klines(symbol, CONTEXT_INTERVAL)

    rsi_15m = compute_rsi(df_15m, RSI_PERIOD)
    rsi_4h = compute_rsi(df_4h, RSI_PERIOD)

    observed_at = datetime.now(ZoneInfo(PARIS_TIMEZONE))

    previous = states.get(symbol, AlertState.NEUTRAL)
    current = classify_rsi(
        rsi_15m,
        RSI_LOWER_LIMIT,
        RSI_UPPER_LIMIT,
    )

    alert_needed = should_alert(previous, current)

    print(
        f"{format_pair(symbol)} | "
        f"RSI 15 min : {rsi_15m:.2f} | "
        f"RSI 4 h : {rsi_4h:.2f} | "
        f"{previous.value} -> {current.value} | "
        f"Alerte : {'oui' if alert_needed else 'non'}"
    )

    if alert_needed:
        message = build_message(
            symbol,
            rsi_15m,
            rsi_4h,
            current,
            observed_at,
        )

        if dry_run:
            print(f"\n--- Aperçu sans envoi ---\n{message}\n")
        else:
            send_telegram_message(message)
            print("Message Telegram envoyé.")

    if not dry_run:
        states[symbol] = current
        save_states(states)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Alertes RSI AAVE et HYPE."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Vérifier sans envoyer ni sauvegarder.",
    )
    args = parser.parse_args()

    try:
        states = load_states()
    except (OSError, ValueError):
        print(
            "Erreur : impossible de lire le fichier d'état. "
            "Exécution interrompue pour éviter les doublons."
        )
        return 1

    failed = False

    for symbol in SYMBOLS:
        try:
            check_symbol(symbol, states, args.dry_run)

        except requests.HTTPError as error:
            failed = True
            response = error.response

            print(
                f"Erreur HTTP de la source de marché pour {symbol}."
            )

            if response is not None:
                print(f"Code HTTP : {response.status_code}")
                print(
                    "Réponse du serveur : "
                    f"{response.text[:1000]}"
                )
            else:
                print("Aucune réponse HTTP disponible.")

        except Exception as error:
            failed = True
            print(
                f"Échec pour {symbol} "
                f"({type(error).__name__}). "
                "Vérifier la source de données, la paire "
                "et la configuration."
            )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())