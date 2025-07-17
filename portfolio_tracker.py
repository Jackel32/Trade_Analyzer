import yfinance as yf

class PortfolioTracker:
    def __init__(self):
        self.portfolio = {}

    def add_position(self, ticker, shares, purchase_price):
        """
        Adds a new position to the portfolio.
        """
        if ticker in self.portfolio:
            self.portfolio[ticker]['shares'] += shares
        else:
            self.portfolio[ticker] = {'shares': shares, 'purchase_price': purchase_price}

    def remove_position(self, ticker, shares):
        """
        Removes a position from the portfolio.
        """
        if ticker in self.portfolio:
            self.portfolio[ticker]['shares'] -= shares
            if self.portfolio[ticker]['shares'] <= 0:
                del self.portfolio[ticker]

    def get_portfolio_performance(self):
        """
        Calculates the overall performance of the portfolio.
        """
        total_value = 0
        total_cost = 0

        for ticker, data in self.portfolio.items():
            stock = yf.Ticker(ticker)
            current_price = stock.history(period="1d")['Close'].iloc[-1]

            total_value += data['shares'] * current_price
            total_cost += data['shares'] * data['purchase_price']

        if total_cost > 0:
            total_return = ((total_value - total_cost) / total_cost) * 100
            return {
                "Total Portfolio Value": f"${total_value:,.2f}",
                "Total Return": f"{total_return:.2f}%"
            }
        return "No positions in the portfolio."
