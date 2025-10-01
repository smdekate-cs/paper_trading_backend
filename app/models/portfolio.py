from datetime import datetime
from app import mongo_client

class Portfolio:
    def __init__(self, user_id, available_margin=100000.0):
        self.user_id = user_id
        self.available_margin = available_margin
        self.utilized_margin = 0.0
        self.total_pnl = 0.0
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def save(self):
        db = mongo_client.paper_trading
        portfolio_data = {
            'user_id': self.user_id,
            'available_margin': self.available_margin,
            'utilized_margin': self.utilized_margin,
            'total_pnl': self.total_pnl,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        return db.portfolios.insert_one(portfolio_data)
    
    @staticmethod
    def find_by_user_id(user_id):
        db = mongo_client.paper_trading
        portfolio_data = db.portfolios.find_one({'user_id': user_id})
        if portfolio_data:
            portfolio = Portfolio(
                user_id=portfolio_data['user_id'],
                available_margin=portfolio_data['available_margin']
            )
            portfolio.utilized_margin = portfolio_data['utilized_margin']
            portfolio.total_pnl = portfolio_data['total_pnl']
            portfolio.created_at = portfolio_data['created_at']
            portfolio.updated_at = portfolio_data['updated_at']
            return portfolio
        return None
    
    def update_margin(self, utilized_margin_change, pnl_change=0):
        db = mongo_client.paper_trading
        self.utilized_margin += utilized_margin_change
        self.available_margin -= utilized_margin_change
        self.total_pnl += pnl_change
        self.updated_at = datetime.utcnow()
        
        db.portfolios.update_one(
            {'user_id': self.user_id},
            {'$set': {
                'available_margin': self.available_margin,
                'utilized_margin': self.utilized_margin,
                'total_pnl': self.total_pnl,
                'updated_at': self.updated_at
            }}
        )
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'available_margin': self.available_margin,
            'utilized_margin': self.utilized_margin,
            'total_pnl': self.total_pnl,
            'margin_utilization_percentage': (self.utilized_margin / (self.available_margin + self.utilized_margin)) * 100 if (self.available_margin + self.utilized_margin) > 0 else 0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }