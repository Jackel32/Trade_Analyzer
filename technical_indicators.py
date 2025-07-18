import pandas as pd

def calculate_moving_average(data, window):
    """
    Calculates the moving average of a stock's closing prices.

    Args:
        data (pd.DataFrame): A DataFrame containing the stock's historical data.
        window (int): The number of periods to use for the moving average calculation.

    Returns:
        pd.Series: A Series containing the moving average values.
    """
    return data['Close'].rolling(window=window).mean()

def calculate_rsi(data, window=14):
    """
    Calculates the Relative Strength Index (RSI) of a stock.

    Args:
        data (pd.DataFrame): A DataFrame containing the stock's historical data.
        window (int): The number of periods to use for the RSI calculation.

    Returns:
        pd.Series: A Series containing the RSI values.
    """
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(data, slow=26, fast=12, signal=9):
    """
    Calculates the Moving Average Convergence Divergence (MACD) of a stock.

    Args:
        data (pd.DataFrame): A DataFrame containing the stock's historical data.
        slow (int): The number of periods for the slow moving average.
        fast (int): The number of periods for the fast moving average.
        signal (int): The number of periods for the signal line.

    Returns:
        tuple: A tuple containing the MACD line, signal line, and MACD histogram.
    """
    exp1 = data['Close'].ewm(span=fast, adjust=False).mean()
    exp2 = data['Close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    return macd, signal_line, histogram

def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    """
    Calculates the Bollinger Bands of a stock.

    Args:
        data (pd.DataFrame): A DataFrame containing the stock's historical data.
        window (int): The number of periods to use for the moving average.
        num_std_dev (int): The number of standard deviations to use for the bands.

    Returns:
        tuple: A tuple containing the upper band, middle band (moving average), and lower band.
    """
    ma = data['Close'].rolling(window=window).mean()
    std_dev = data['Close'].rolling(window=window).std()
    upper_band = ma + (std_dev * num_std_dev)
    lower_band = ma - (std_dev * num_std_dev)
    return upper_band, ma, lower_band

def calculate_obv(data):
    """
    Calculates the On-Balance Volume (OBV) of a stock.

    Args:
        data (pd.DataFrame): A DataFrame containing the stock's historical data.

    Returns:
        pd.Series: A Series containing the OBV values.
    """
    obv = (data['Volume'] * (~data['Close'].diff().le(0) * 2 - 1)).cumsum()
    return obv

def calculate_stochastic_oscillator(data, window=14):
    """
    Calculates the Stochastic Oscillator of a stock.

    Args:
        data (pd.DataFrame): A DataFrame containing the stock's historical data.
        window (int): The number of periods to use for the calculation.

    Returns:
        pd.Series: A Series containing the Stochastic Oscillator values.
    """
    low_min = data['Low'].rolling(window=window).min()
    high_max = data['High'].rolling(window=window).max()
    stochastic = 100 * ((data['Close'] - low_min) / (high_max - low_min))
    return stochastic
