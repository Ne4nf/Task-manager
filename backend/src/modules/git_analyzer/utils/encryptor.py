"""
Token Encryption Utility
Encrypts/decrypts GitHub access tokens using Fernet symmetric encryption
"""
import os
from cryptography.fernet import Fernet
from typing import Optional


class TokenEncryptor:
    """Handles encryption and decryption of sensitive tokens"""
    
    def __init__(self):
        """Initialize encryptor with encryption key from environment"""
        encryption_key = os.getenv("ENCRYPTION_KEY")
        
        if not encryption_key:
            # Generate a new key if not exists (for development)
            # In production, this should be set in environment variables
            encryption_key = Fernet.generate_key().decode()
            print(f"⚠️  WARNING: No ENCRYPTION_KEY found. Generated temporary key: {encryption_key}")
            print("    Add this to your .env file for production!")
        
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
            
        self.cipher_suite = Fernet(encryption_key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string
        
        Args:
            plaintext: The string to encrypt (e.g., GitHub access token)
        
        Returns:
            Encrypted string (base64 encoded)
        """
        if not plaintext:
            return ""
        
        encrypted_bytes = self.cipher_suite.encrypt(plaintext.encode())
        return encrypted_bytes.decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt an encrypted string
        
        Args:
            encrypted_text: The encrypted string to decrypt
        
        Returns:
            Decrypted plaintext string
        """
        if not encrypted_text:
            return ""
        
        try:
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_text.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt token: {str(e)}")


# Global encryptor instance
_encryptor: Optional[TokenEncryptor] = None


def get_encryptor() -> TokenEncryptor:
    """Get or create the global encryptor instance"""
    global _encryptor
    if _encryptor is None:
        _encryptor = TokenEncryptor()
    return _encryptor


# Convenience functions
def encrypt_token(token: str) -> str:
    """Encrypt a token string"""
    return get_encryptor().encrypt(token)


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token string"""
    return get_encryptor().decrypt(encrypted_token)
