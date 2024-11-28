import os
from cryptography.fernet import Fernet

class Security:
    def __init__(self):
        self.key = self.load_or_generate_key()
        self.cipher_suite = Fernet(self.key)

    def load_or_generate_key(self):
        key_file = 'crypto.key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as file:
                return file.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as file:
                file.write(key)
            return key

    def encrypt(self, data: str) -> str:
        return self.cipher_suite.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        # Implement your API key validation logic here
        # This is a placeholder implementation
        return len(api_key) == 32  # Example: check if API key is 32 characters long

    @staticmethod
    def validate_order(order: dict) -> bool:
        # Implement your order validation logic here
        # This is a placeholder implementation
        required_fields = ['symbol', 'side', 'type', 'amount']
        return all(field in order for field in required_fields)
