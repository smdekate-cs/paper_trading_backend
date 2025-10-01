from datetime import datetime
from app import mongo_client
import bcrypt

class User:
    def __init__(self, client_id, name, email, phone, password_hash):
        self.client_id = client_id
        self.name = name
        self.email = email
        self.phone = phone
        self.password_hash = password_hash
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def save(self):
        db = mongo_client.paper_trading
        user_data = {
            'client_id': self.client_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'password_hash': self.password_hash,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        return db.users.insert_one(user_data)
    
    @staticmethod
    def find_by_email(email):
        db = mongo_client.paper_trading
        user_data = db.users.find_one({'email': email})
        if user_data:
            return User(
                client_id=user_data['client_id'],
                name=user_data['name'],
                email=user_data['email'],
                phone=user_data['phone'],
                password_hash=user_data['password_hash']
            )
        return None
    
    @staticmethod
    def find_by_client_id(client_id):
        db = mongo_client.paper_trading
        user_data = db.users.find_one({'client_id': client_id})
        if user_data:
            return User(
                client_id=user_data['client_id'],
                name=user_data['name'],
                email=user_data['email'],
                phone=user_data['phone'],
                password_hash=user_data['password_hash']
            )
        return None
    
    @staticmethod
    def email_exists(email):
        db = mongo_client.paper_trading
        return db.users.find_one({'email': email}) is not None