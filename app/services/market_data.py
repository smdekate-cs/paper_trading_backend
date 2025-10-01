import requests
import json
from datetime import datetime
from app import redis_client
import time

class MarketDataService:
    def __init__(self):
        self.base_url = "https://api.upstox.com/v2"  # Example API
        self.api_key = "your_api_key_here"  # Should be in environment variables
    
    def get_live_price(self, symbol):
        """Get live price for a symbol"""
        try:
            # Check cache first
            cached_price = redis_client.get(f"price:{symbol}")
            if cached_price:
                return json.loads(cached_price)
            
            # Simulate API call (replace with actual API integration)
            # For demo purposes, we'll use mock data
            mock_prices = {
                "NIFTY50": 19500 + (datetime.now().minute % 10) * 10,
                "SENSEX": 65000 + (datetime.now().minute % 10) * 50,
                "RELIANCE": 2450 + (datetime.now().minute % 10) * 5,
                "TCS": 3450 + (datetime.now().minute % 10) * 3
            }
            
            price_data = {
                'symbol': symbol,
                'price': mock_prices.get(symbol, 1000),
                'timestamp': datetime.utcnow().isoformat(),
                'change': 2.5,  # Mock change percentage
                'volume': 1000000
            }
            
            # Cache for 5 seconds
            redis_client.setex(f"price:{symbol}", 5, json.dumps(price_data))
            
            return price_data
            
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return None
    
    def get_index_data(self):
        """Get Nifty 50 and Sensex data"""
        nifty_data = self.get_live_price("NIFTY50")
        sensex_data = self.get_live_price("SENSEX")
        
        return {
            'nifty50': nifty_data,
            'sensex': sensex_data
        }

market_data_service = MarketDataService()