"""
Security module for user data protection
"""
import os
import json
import hashlib
import secrets
import bcrypt
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import re

class SecurityManager:
    def __init__(self):
        # Generate or load encryption key
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
    def _get_or_create_encryption_key(self):
        """Get or create encryption key for data protection"""
        key_file = '.encryption_key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        if isinstance(data, dict):
            data = json.dumps(data)
        return self.cipher_suite.encrypt(data.encode('utf-8')).decode('utf-8')
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        try:
            decrypted = self.cipher_suite.decrypt(encrypted_data.encode('utf-8'))
            return json.loads(decrypted.decode('utf-8'))
        except:
            return None
    
    def validate_phone(self, phone):
        """Validate phone number format"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check if it's a valid length (7-15 digits)
        return 7 <= len(digits_only) <= 15
    
    def validate_name(self, name):
        """Validate name format"""
        # Allow letters, spaces, hyphens, and apostrophes
        return bool(re.match(r"^[a-zA-Z\s\-']+$", name)) and 2 <= len(name) <= 50
    
    def sanitize_input(self, text):
        """Sanitize user input"""
        if not text:
            return ""
        # Remove potentially dangerous characters
        text = re.sub(r'[<>"\']', '', str(text))
        return text.strip()
    
    def generate_secure_token(self, length=32):
        """Generate secure random token"""
        return secrets.token_urlsafe(length)
    
    def validate_session(self, session_data):
        """Validate session data"""
        if not session_data:
            return False
        
        # Check if session has required fields
        required_fields = ['user_id', 'created_at']
        if not all(field in session_data for field in required_fields):
            return False
        
        # Check if session is not too old (24 hours)
        try:
            created_at = datetime.fromisoformat(session_data['created_at'])
            if datetime.now() - created_at > timedelta(hours=24):
                return False
        except:
            return False
        
        return True

class SecureUserManager:
    def __init__(self):
        self.security = SecurityManager()
        self.users_file = 'users_secure.json'
        self.sessions_file = 'sessions_secure.json'
    
    def load_users(self):
        """Load users from encrypted storage"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r') as f:
                    encrypted_data = f.read()
                    return self.security.decrypt_data(encrypted_data) or {}
            return {}
        except:
            return {}
    
    def save_users(self, users):
        """Save users to encrypted storage"""
        try:
            encrypted_data = self.security.encrypt_data(users)
            with open(self.users_file, 'w') as f:
                f.write(encrypted_data)
            return True
        except:
            return False
    
    def create_user(self, name, phone, password, preferences):
        """Create a new user with security measures"""
        # Validate inputs
        if not self.security.validate_name(name):
            return {'error': 'Invalid name format'}
        
        if not self.security.validate_phone(phone):
            return {'error': 'Invalid phone number format'}
        
        if not password or len(password) < 6:
            return {'error': 'Password must be at least 6 characters'}
        
        # Sanitize inputs
        name = self.security.sanitize_input(name)
        phone = self.security.sanitize_input(phone)
        
        # Load existing users
        users = self.load_users()
        
        # Check if phone already exists
        for user_id, user_data in users.items():
            if user_data.get('phone') == phone:
                return {'error': 'Phone number already registered'}
        
        # Create new user
        user_id = self.security.generate_secure_token(16)
        hashed_password = self.security.hash_password(password)
        
        users[user_id] = {
            'name': name,
            'phone': phone,
            'password_hash': hashed_password,
            'preferences': preferences,
            'created_at': datetime.now().isoformat(),
            'last_login': None,
            'login_attempts': 0,
            'locked_until': None,
            'liked_topics': {},
            'passed_topics': {}
        }
        
        if self.save_users(users):
            return {'success': True, 'user_id': user_id}
        else:
            return {'error': 'Failed to save user data'}
    
    def authenticate_user(self, phone, password):
        """Authenticate user with security checks"""
        users = self.load_users()
        
        # Find user by phone
        user_id = None
        user_data = None
        for uid, data in users.items():
            if data.get('phone') == phone:
                user_id = uid
                user_data = data
                break
        
        if not user_id or not user_data:
            return {'error': 'Invalid credentials'}
        
        # Check if account is locked
        if user_data.get('locked_until'):
            locked_until = datetime.fromisoformat(user_data['locked_until'])
            if datetime.now() < locked_until:
                return {'error': 'Account temporarily locked due to too many failed attempts'}
        
        # Verify password
        if not self.security.verify_password(password, user_data['password_hash']):
            # Increment login attempts
            user_data['login_attempts'] = user_data.get('login_attempts', 0) + 1
            
            # Lock account after 5 failed attempts for 30 minutes
            if user_data['login_attempts'] >= 5:
                user_data['locked_until'] = (datetime.now() + timedelta(minutes=30)).isoformat()
            
            self.save_users(users)
            return {'error': 'Invalid credentials'}
        
        # Reset login attempts on successful login
        user_data['login_attempts'] = 0
        user_data['locked_until'] = None
        user_data['last_login'] = datetime.now().isoformat()
        
        self.save_users(users)
        return {'success': True, 'user_id': user_id, 'user_data': user_data}
    
    def update_user_preferences(self, user_id, preferences):
        """Update user preferences securely"""
        users = self.load_users()
        
        if user_id not in users:
            return {'error': 'User not found'}
        
        # Validate preferences
        valid_topics = {'inflation', 'technology', 'politics', 'health', 'business', 'science', 'sports', 'environment'}
        if not all(topic in valid_topics for topic in preferences):
            return {'error': 'Invalid topic selected'}
        
        users[user_id]['preferences'] = preferences
        
        if self.save_users(users):
            return {'success': True}
        else:
            return {'error': 'Failed to update preferences'}

# Global security manager instance
security_manager = SecureUserManager()
