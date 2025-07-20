import unittest
from stock_analyzer import StockAnalyzer

class TestStockAnalyzer(unittest.TestCase):
    def test_get_sell_prices(self):
        analyzer = StockAnalyzer("AAPL")
        purchase_price = 150.00
        sell_prices = analyzer.get_sell_prices(purchase_price)
        self.assertEqual(sell_prices["stop_loss"], "135.00")
        self.assertEqual(sell_prices["take_profit"], "180.00")

if __name__ == "__main__":
    unittest.main()
