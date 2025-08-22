import pandas as pd
import pandas_ta as ta
def add_base_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['ema20'] = ta.ema(df['close'], length=20)
    df['ema50'] = ta.ema(df['close'], length=50)
    adx = ta.adx(df['high'], df['low'], df['close'], length=14)
    df['adx'] = adx['ADX_14']
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    bb = ta.bbands(df['close'], length=20, std=2)
    df['bb_low'] = bb['BBL_20_2.0']
    df['bb_mid'] = bb['BBM_20_2.0']
    df['bb_high'] = bb['BBU_20_2.0']
    df['rsi'] = ta.rsi(df['close'], length=14)
    return df
