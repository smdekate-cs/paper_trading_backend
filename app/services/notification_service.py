import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import requests
from app import redis_client
import json

class NotificationService:
    def __init__(self):
        self.sms_api_key = "your_sms_api_key"  # Should be in environment variables
        self.sms_url = "https://api.sms_service.com/send"
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_sender = "noreply@papertrading.com"
        self.email_password = "your_email_password"  # Should be in environment variables
    
    def send_sms(self, phone_number, message):
        """Send SMS notification"""
        try:
            # Mock SMS implementation - replace with actual SMS service
            print(f"SMS to {phone_number}: {message}")
            
            # Actual implementation would look like:
            # payload = {
            #     'api_key': self.sms_api_key,
            #     'to': phone_number,
            #     'message': message
            # }
            # response = requests.post(self.sms_url, json=payload)
            # return response.status_code == 200
            
            return True  # Mock success
            
        except Exception as e:
            print(f"SMS sending failed: {e}")
            return False
    
    def send_email(self, email, subject, message):
        """Send email notification"""
        try:
            # Mock email implementation - replace with actual email service
            print(f"Email to {email} - {subject}: {message}")
            
            # Actual implementation would look like:
            # msg = MimeMultipart()
            # msg['From'] = self.email_sender
            # msg['To'] = email
            # msg['Subject'] = subject
            # msg.attach(MimeText(message, 'plain'))
            
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()
            # server.login(self.email_sender, self.email_password)
            # server.send_message(msg)
            # server.quit()
            
            return True  # Mock success
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def notify_trade_creation(self, user_email, user_phone, trade_details):
        """Notify user about trade creation"""
        message = f"Trade created: {trade_details['symbol']} {trade_details['trade_type']} {trade_details['quantity']} shares at {trade_details['entry_price']}"
        
        if user_phone:
            self.send_sms(user_phone, message)
        
        if user_email:
            self.send_email(user_email, "Trade Created", message)
    
    def notify_trade_exit(self, user_email, user_phone, trade_details):
        """Notify user about trade exit"""
        pnl_text = "profit" if trade_details['pnl'] > 0 else "loss"
        message = f"Trade exited: {trade_details['symbol']} at {trade_details['exit_price']} with {pnl_text} of {abs(trade_details['pnl'])}"
        
        if user_phone:
            self.send_sms(user_phone, message)
        
        if user_email:
            self.send_email(user_email, "Trade Exited", message)
    
    def notify_stop_loss_hit(self, user_email, user_phone, trade_details):
        """Notify user about stop-loss hit"""
        message = f"Stop-loss triggered: {trade_details['symbol']} exited at {trade_details['exit_price']} with PnL: {trade_details['pnl']}"
        
        if user_phone:
            self.send_sms(user_phone, message)
        
        if user_email:
            self.send_email(user_email, "Stop-Loss Triggered", message)
    
    def notify_target_hit(self, user_email, user_phone, trade_details):
        """Notify user about target hit"""
        message = f"Target achieved: {trade_details['symbol']} exited at {trade_details['exit_price']} with PnL: {trade_details['pnl']}"
        
        if user_phone:
            self.send_sms(user_phone, message)
        
        if user_email:
            self.send_email(user_email, "Target Achieved", message)

notification_service = NotificationService()