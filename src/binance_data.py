import pandas as pd
import requests


BINANCE_KLINES_URL = (
    "https://data-api.binance.vision/api/v3/klines"
)

COLUMNS = [
    "open_time",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "close_time",
    "quote_volume",
    "trades",
    "taker_buy_base",
    "taker_buy_quote",
    "ignore",
]


def get_klines(
    symbol: str,
    interval: str,
    limit: int = 100,
) -> pd.DataFrame:
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }

    response = requests.get(
        BINANCE_KLINES_URL,
        params=params,
        timeout=20,
    )
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list) or not data:
        raise ValueError(
            f"Aucune liste de bougies valide pour {symbol} "
            f"sur l'intervalle {interval}."
        )

    df = pd.DataFrame(data, columns=COLUMNS)

    numeric_columns = [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="raise",
        )

    return df