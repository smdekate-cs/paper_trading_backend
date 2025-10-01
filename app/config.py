import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # MongoDB
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/paper_trading'
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Market Data API
    MARKET_DATA_API_KEY = os.environ.get('MARKET_DATA_API_KEY', '')
    MARKET_DATA_BASE_URL = 'https://api.upstox.com/v2'  # Example API