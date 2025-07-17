import yfinance as yf

class StockScreener:
    def __init__(self, tickers):
        self.tickers = tickers

    def screen_stocks(self, criteria):
        """
        Screens stocks based on a given set of criteria.
        """
        screened_stocks = []
        for ticker in self.tickers:
            stock = yf.Ticker(ticker)
            info = stock.info

            passes_criteria = True
            for key, value in criteria.items():
                if key == "market_cap":
                    if info.get("marketCap", 0) < value:
                        passes_criteria = False
                        break
                elif key == "pe_ratio":
                    if info.get("trailingPE", float('inf')) > value:
                        passes_criteria = False
                        break
                elif key == "dividend_yield":
                    if info.get("dividendYield", 0) < value:
                        passes_criteria = False
                        break

            if passes_criteria:
                screened_stocks.append(ticker)

        return screened_stocks
