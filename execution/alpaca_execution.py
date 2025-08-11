import alpaca_trade_api as tradeapi
import os
from dotenv import load_dotenv

load_dotenv()

class AlpacaExecution:
    def __init__(self):
        self.api_key = os.getenv("ALPACA_API_KEY")
        self.api_secret = os.getenv("ALPACA_API_SECRET")
        self.base_url = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

        # Ensure the base_url is clean
        if self.base_url.endswith('/v2'):
            self.base_url = self.base_url[:-3]

        self.api = tradeapi.REST(self.api_key, self.api_secret, self.base_url, api_version='v2')

    def get_account_info(self):
        """
        Retrieves and returns account information.
        """
        try:
            account = self.api.get_account()
            return account
        except Exception as e:
            print(f"Error getting account information: {e}")
            return None

    def submit_order(self, symbol, qty, side, order_type, time_in_force):
        """
        Submits a new order.
        """
        try:
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=order_type,
                time_in_force=time_in_force
            )
            return order
        except Exception as e:
            print(f"Error submitting order: {e}")
            return None

    def get_all_orders(self):
        """
        Retrieves and returns all orders.
        """
        try:
            orders = self.api.list_orders()
            return orders
        except Exception as e:
            print(f"Error getting orders: {e}")
            return None

    def get_asset(self, symbol):
        """
        Retrieves and returns a specific asset.
        """
        try:
            asset = self.api.get_asset(symbol)
            return asset
        except Exception as e:
            print(f"Error getting asset {symbol}: {e}")
            return None

if __name__ == '__main__':
    # Example usage
    alpaca = AlpacaExecution()
    
    # Get account information
    account_info = alpaca.get_account_info()
    if account_info:
        print("Account Information:")
        print(f"  Account Number: {account_info.account_number}")
        print(f"  Buying Power: {account_info.buying_power}")
        print(f"  Equity: {account_info.equity}")

    # Example: Submit a paper trading order
    # Note: This will fail if you don't have valid paper trading keys.
    # order = alpaca.submit_order(
    #     symbol='AAPL',
    #     qty=1,
    #     side='buy',
    #     order_type='market',
    #     time_in_force='gtc'
    # )
    # if order:
    #     print("\nOrder Submitted:")
    #     print(f"  ID: {order.id}")
    #     print(f"  Symbol: {order.symbol}")
    #     print(f"  Status: {order.status}")

    # Get all orders
    all_orders = alpaca.get_all_orders()
    if all_orders:
        print("\nAll Orders:")
        for order in all_orders:
            print(f"  - ID: {order.id}, Symbol: {order.symbol}, Status: {order.status}")

    # Get a specific asset
    asset_info = alpaca.get_asset('AAPL')
    if asset_info:
        print("\nAsset Information for AAPL:")
        print(f"  Symbol: {asset_info.symbol}")
        print(f"  Tradable: {asset_info.tradable}")
        print(f"  Exchange: {asset_info.exchange}")
