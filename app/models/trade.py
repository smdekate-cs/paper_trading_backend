from datetime import datetime
from enum import Enum
from app import mongo_client

class TradeType(Enum):
    BUY = "BUY"
    SELL = "SELL"

class TradeStatus(Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    STOP_LOSS_HIT = "STOP_LOSS_HIT"
    TARGET_HIT = "TARGET_HIT"

class Trade:
    def __init__(self, user_id, symbol, trade_type, quantity, entry_price, 
                 margin_used, stop_loss=None, target_price=None):
        self.trade_id = None
        self.user_id = user_id
        self.symbol = symbol
        self.trade_type = TradeType(trade_type)
        self.quantity = quantity
        self.entry_price = entry_price
        self.margin_used = margin_used
        self.stop_loss = stop_loss
        self.target_price = target_price
        self.current_price = entry_price
        self.pnl = 0.0
        self.status = TradeStatus.ACTIVE
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.closed_at = None
        self.exit_price = None
    
    def save(self):
        db = mongo_client.paper_trading
        trade_data = {
            'user_id': self.user_id,
            'symbol': self.symbol,
            'trade_type': self.trade_type.value,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'margin_used': self.margin_used,
            'stop_loss': self.stop_loss,
            'target_price': self.target_price,
            'current_price': self.current_price,
            'pnl': self.pnl,
            'status': self.status.value,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'closed_at': self.closed_at,
            'exit_price': self.exit_price
        }
        result = db.trades.insert_one(trade_data)
        self.trade_id = str(result.inserted_id)
        return result
    
    def update_price(self, current_price):
        db = mongo_client.paper_trading
        self.current_price = current_price
        
        # Calculate PnL
        if self.trade_type == TradeType.BUY:
            self.pnl = (current_price - self.entry_price) * self.quantity
        else:  # SELL
            self.pnl = (self.entry_price - current_price) * self.quantity
        
        self.updated_at = datetime.utcnow()
        
        db.trades.update_one(
            {'_id': self.trade_id},
            {'$set': {
                'current_price': self.current_price,
                'pnl': self.pnl,
                'updated_at': self.updated_at
            }}
        )
    
    def close_trade(self, exit_price, status=TradeStatus.CLOSED):
        db = mongo_client.paper_trading
        self.exit_price = exit_price
        self.status = status
        self.closed_at = datetime.utcnow()
        
        # Calculate final PnL
        if self.trade_type == TradeType.BUY:
            self.pnl = (exit_price - self.entry_price) * self.quantity
        else:  # SELL
            self.pnl = (self.entry_price - exit_price) * self.quantity
        
        db.trades.update_one(
            {'_id': self.trade_id},
            {'$set': {
                'exit_price': self.exit_price,
                'status': self.status.value,
                'pnl': self.pnl,
                'closed_at': self.closed_at,
                'updated_at': self.updated_at
            }}
        )
    
    def check_auto_exit(self, current_price):
        if self.status != TradeStatus.ACTIVE:
            return False
        
        if self.stop_loss and (
            (self.trade_type == TradeType.BUY and current_price <= self.stop_loss) or
            (self.trade_type == TradeType.SELL and current_price >= self.stop_loss)
        ):
            self.close_trade(current_price, TradeStatus.STOP_LOSS_HIT)
            return True
        
        if self.target_price and (
            (self.trade_type == TradeType.BUY and current_price >= self.target_price) or
            (self.trade_type == TradeType.SELL and current_price <= self.target_price)
        ):
            self.close_trade(current_price, TradeStatus.TARGET_HIT)
            return True
        
        return False
    
    @staticmethod
    def find_by_id(trade_id):
        db = mongo_client.paper_trading
        from bson.objectid import ObjectId
        trade_data = db.trades.find_one({'_id': ObjectId(trade_id)})
        return Trade.from_dict(trade_data) if trade_data else None
    
    @staticmethod
    def find_active_trades_by_user(user_id):
        db = mongo_client.paper_trading
        trades_data = db.trades.find({
            'user_id': user_id,
            'status': 'ACTIVE'
        })
        return [Trade.from_dict(trade) for trade in trades_data]
    
    @staticmethod
    def find_all_trades_by_user(user_id):
        db = mongo_client.paper_trading
        trades_data = db.trades.find({'user_id': user_id}).sort('created_at', -1)
        return [Trade.from_dict(trade) for trade in trades_data]
    
    @staticmethod
    def from_dict(trade_data):
        trade = Trade(
            user_id=trade_data['user_id'],
            symbol=trade_data['symbol'],
            trade_type=trade_data['trade_type'],
            quantity=trade_data['quantity'],
            entry_price=trade_data['entry_price'],
            margin_used=trade_data['margin_used'],
            stop_loss=trade_data.get('stop_loss'),
            target_price=trade_data.get('target_price')
        )
        trade.trade_id = str(trade_data['_id'])
        trade.current_price = trade_data['current_price']
        trade.pnl = trade_data['pnl']
        trade.status = TradeStatus(trade_data['status'])
        trade.created_at = trade_data['created_at']
        trade.updated_at = trade_data['updated_at']
        trade.closed_at = trade_data.get('closed_at')
        trade.exit_price = trade_data.get('exit_price')
        return trade
    
    def to_dict(self):
        return {
            'trade_id': self.trade_id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'trade_type': self.trade_type.value,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'margin_used': self.margin_used,
            'stop_loss': self.stop_loss,
            'target_price': self.target_price,
            'pnl': self.pnl,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'exit_price': self.exit_price
        }