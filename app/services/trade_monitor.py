import threading
import time
from app import mongo_client, redis_client
from app.models.trade import Trade
from app.services.market_data import market_data_service
from app.models.portfolio import Portfolio

class TradeMonitor:
    def __init__(self):
        self.running = False
        self.monitor_thread = None
    
    def start_monitoring(self):
        """Start background thread for monitoring trades"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("Trade monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("Trade monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                self._check_active_trades()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"Error in trade monitoring: {e}")
                time.sleep(10)
    
    def _check_active_trades(self):
        """Check all active trades for auto-exit conditions"""
        db = mongo_client.paper_trading
        active_trades = db.trades.find({'status': 'ACTIVE'})
        
        for trade_data in active_trades:
            try:
                trade = Trade.from_dict(trade_data)
                current_price_data = market_data_service.get_live_price(trade.symbol)
                
                if current_price_data:
                    current_price = current_price_data['price']
                    
                    # Update current price and PnL
                    trade.update_price(current_price)
                    
                    # Check for auto-exit conditions
                    if trade.check_auto_exit(current_price):
                        print(f"Trade {trade.trade_id} auto-closed: {trade.status.value}")
                        
                        # Update portfolio margin
                        portfolio = Portfolio.find_by_user_id(trade.user_id)
                        if portfolio:
                            portfolio.update_margin(-trade.margin_used, trade.pnl)
                            
            except Exception as e:
                print(f"Error monitoring trade {trade_data.get('_id')}: {e}")

trade_monitor = TradeMonitor()