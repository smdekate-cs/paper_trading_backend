from app import create_app, socketio
from app.services.trade_monitor import trade_monitor
import os

app = create_app()

if __name__ == '__main__':
    # Start trade monitoring
    trade_monitor.start_monitoring()
    
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)