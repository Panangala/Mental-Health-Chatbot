"""
Authentication Module
Handles user registration, login, JWT tokens, and session management
"""

import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from functools import wraps
from flask import request, jsonify
import hashlib
import secrets

logger = logging.getLogger(__name__)


class PasswordManager:
    """Handles password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using SHA256
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password with salt
        """
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        return f"{salt}${pwd_hash}"
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            password: Plain text password
            hashed: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            salt, pwd_hash = hashed.split('$')
            new_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
            return new_hash == pwd_hash
        except:
            return False


class JWTManager:
    """Handles JWT token creation and verification"""
    
    def __init__(self, secret_key: str, algorithm: str = 'HS256', expiration_hours: int = 24):
        """
        Initialize JWT Manager
        
        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT algorithm (default: HS256)
            expiration_hours: Token expiration time in hours
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours
    
    def create_token(self, user_id: int, username: str, email: str) -> str:
        """
        Create a JWT token
        
        Args:
            user_id: User ID
            username: Username
            email: User email
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'email': email,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=self.expiration_hours)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Token created for user: {username}")
        return token
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            logger.debug(f"Token verified for user: {payload.get('username')}")
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def extract_token_from_request(self) -> Optional[str]:
        """
        Extract JWT token from Authorization header
        
        Returns:
            Token string or None
        """
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return None
        
        return auth_header[7:]  # Remove 'Bearer ' prefix


class AuthenticationService:
    """Main authentication service"""
    
    def __init__(self, db_connection, jwt_manager: JWTManager):
        """
        Initialize Authentication Service
        
        Args:
            db_connection: Database connection object
            jwt_manager: JWT Manager instance
        """
        self.db = db_connection
        self.jwt = jwt_manager
        self.pwd_manager = PasswordManager()
    
    def register_user(self, username: str, email: str, password: str, 
                     first_name: str = '', last_name: str = '') -> Tuple[bool, str, Optional[Dict]]:
        """
        Register a new user
        
        Args:
            username: Username
            email: Email address
            password: Password
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            Tuple of (success, message, user_data)
        """
        try:
            # Check if user exists
            cursor = self.db.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s OR username = %s", (email, username))
            
            if cursor.fetchone():
                return False, "User already exists", None
            
            # Hash password
            password_hash = self.pwd_manager.hash_password(password)
            
            # Insert user
            cursor.execute(
                """INSERT INTO users (username, email, password_hash, first_name, last_name)
                   VALUES (%s, %s, %s, %s, %s)
                   RETURNING id, username, email, first_name, last_name""",
                (username, email, password_hash, first_name, last_name)
            )
            
            user_data = cursor.fetchone()
            self.db.commit()
            
            logger.info(f"User registered: {username}")
            return True, "User registered successfully", {
                'id': user_data[0],
                'username': user_data[1],
                'email': user_data[2],
                'first_name': user_data[3],
                'last_name': user_data[4]
            }
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Registration error: {str(e)}")
            return False, f"Registration failed: {str(e)}", None
    
    def login_user(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Login a user
        
        Args:
            email: User email
            password: User password
            
        Returns:
            Tuple of (success, message, auth_data)
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(
                "SELECT id, username, email, password_hash, is_active FROM users WHERE email = %s",
                (email,)
            )
            
            user = cursor.fetchone()
            
            if not user:
                return False, "Invalid email or password", None
            
            user_id, username, user_email, password_hash, is_active = user
            
            if not is_active:
                return False, "User account is inactive", None
            
            # Verify password
            if not self.pwd_manager.verify_password(password, password_hash):
                return False, "Invalid email or password", None
            
            # Update last login
            cursor.execute(
                "UPDATE users SET last_login = NOW() WHERE id = %s",
                (user_id,)
            )
            self.db.commit()
            
            # Create JWT token
            token = self.jwt.create_token(user_id, username, user_email)
            
            logger.info(f"User logged in: {username}")
            return True, "Login successful", {
                'token': token,
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': user_email
                }
            }
        
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False, f"Login failed: {str(e)}", None
    
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """
        Get user profile
        
        Args:
            user_id: User ID
            
        Returns:
            User profile data or None
        """
        try:
            cursor = self.db.cursor()
            cursor.execute(
                """SELECT id, username, email, first_name, last_name, 
                          created_at, total_conversations, avg_mood_change, is_admin
                   FROM users WHERE id = %s""",
                (user_id,)
            )
            
            user = cursor.fetchone()
            
            if not user:
                return None
            
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'first_name': user[3],
                'last_name': user[4],
                'created_at': user[5].isoformat() if user[5] else None,
                'total_conversations': user[6],
                'avg_mood_change': user[7],
                'is_admin': user[8]
            }
        
        except Exception as e:
            logger.error(f"Profile retrieval error: {str(e)}")
            return None


class AuthDecorator:
    """Decorator for protecting routes with JWT authentication"""
    
    @staticmethod
    def require_auth(jwt_manager: JWTManager):
        """
        Decorator to require JWT authentication
        
        Usage:
            @require_auth(jwt_manager)
            def protected_route():
                pass
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                token = jwt_manager.extract_token_from_request()
                
                if not token:
                    return jsonify({'success': False, 'message': 'Missing authentication token'}), 401
                
                payload = jwt_manager.verify_token(token)
                
                if not payload:
                    return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401
                
                # Store user info in request context
                request.user_id = payload['user_id']
                request.username = payload['username']
                request.email = payload['email']
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator