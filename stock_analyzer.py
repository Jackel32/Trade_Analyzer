import yfinance as yf

from technical_indicators import (
    calculate_moving_average,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_obv,
    calculate_stochastic_oscillator,
)

class StockAnalyzer:
    def __init__(self, ticker):
        self.ticker = ticker
        self.stock = yf.Ticker(ticker)

    def get_all_info(self):
        """
        Retrieves all available information for the stock for debugging purposes.
        """
        info = self.stock.info
        print("Available information from yfinance:")
        for key, value in info.items():
            print(f"- {key}: {value}")

    def get_financial_metrics(self):
        """
        Retrieves key financial metrics for the stock.
        """
        financials = self.stock.financials
        if financials is not None and not financials.empty:
            return financials
        return "Financial data not available."

    def get_technical_indicators(self):
        """
        Calculates key technical indicators for the stock.
        """
        hist = self.stock.history(period="1y")
        if not hist.empty:
            ma50 = calculate_moving_average(hist, 50).iloc[-1]
            ma200 = calculate_moving_average(hist, 200).iloc[-1]
            rsi = calculate_rsi(hist).iloc[-1]
            macd, signal_line, _ = calculate_macd(hist)
            upper_band, _, lower_band = calculate_bollinger_bands(hist)
            obv = calculate_obv(hist).iloc[-1]
            stochastic = calculate_stochastic_oscillator(hist).iloc[-1]

            return {
                "50-Day MA": f"{ma50:.2f}",
                "200-Day MA": f"{ma200:.2f}",
                "RSI (14)": f"{rsi:.2f}",
                "MACD": f"{macd.iloc[-1]:.2f}",
                "Signal Line": f"{signal_line.iloc[-1]:.2f}",
                "Bollinger Upper": f"{upper_band.iloc[-1]:.2f}",
                "Bollinger Lower": f"{lower_band.iloc[-1]:.2f}",
                "OBV": f"{obv:,.0f}",
                "Stochastic Oscillator": f"{stochastic:.2f}",
            }
        return "Technical data not available."

    def get_market_sentiment(self):
        """
        Retrieves news and sentiment analysis for the stock.
        """
        news = self.stock.news
        if news:
            return news
        return "Market sentiment data not available."

    def get_confidence_score(self):
        """
        Calculates a confidence score for the stock based on a combination of
        technical and fundamental factors.
        """
        score = 0

        # Technical factors
        hist = self.stock.history(period="1y")
        if not hist.empty:
            ma50 = calculate_moving_average(hist, 50).iloc[-1]
            ma200 = calculate_moving_average(hist, 200).iloc[-1]
            rsi = calculate_rsi(hist).iloc[-1]

            if ma50 > ma200:
                score += 1
            if rsi < 70 and rsi > 30:
                score += 1

        # Fundamental factors
        info = self.stock.info
        if info.get("trailingPE", float('inf')) < 25:
            score += 1
        if info.get("forwardPE", float('inf')) < info.get("trailingPE", float('inf')):
            score += 1
        if info.get("dividendYield", 0) > 0:
            score += 1

        return f"{(score / 5) * 100:.2f}%"

    def get_sell_prices(self, purchase_price):
        """
        Calculates the stop loss and take profit prices for the stock.
        """
        stop_loss = purchase_price * 0.9
        take_profit = purchase_price * 1.2
        return {
            "stop_loss": f"{stop_loss:.2f}",
            "take_profit": f"{take_profit:.2f}",
        }
