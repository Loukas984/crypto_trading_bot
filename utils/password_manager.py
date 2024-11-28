
import re
import time
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox

class PasswordManager:
    def __init__(self, min_length=12, require_special_char=True, require_number=True, require_uppercase=True, max_attempts=3, lockout_time=300):
        self.min_length = min_length
        self.require_special_char = require_special_char
        self.require_number = require_number
        self.require_uppercase = require_uppercase
        self.max_attempts = max_attempts
        self.lockout_time = lockout_time
        self.attempts = 0
        self.last_attempt_time = 0

    def validate_password(self, password):
        if len(password) < self.min_length:
            return False, f"Password must be at least {self.min_length} characters long."
        
        if self.require_special_char and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character."
        
        if self.require_number and not re.search(r"\d", password):
            return False, "Password must contain at least one number."
        
        if self.require_uppercase and not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter."
        
        return True, "Password is valid."

    def check_lockout(self):
        if self.attempts >= self.max_attempts:
            time_since_last_attempt = time.time() - self.last_attempt_time
            if time_since_last_attempt < self.lockout_time:
                return True, f"Account is locked. Please try again in {int(self.lockout_time - time_since_last_attempt)} seconds."
            else:
                self.attempts = 0
        return False, ""

    def prompt_for_password(self, parent=None, is_new=False):
        action = "Enter new" if is_new else "Enter"
        while True:
            is_locked, message = self.check_lockout()
            if is_locked:
                QMessageBox.warning(parent, "Account Locked", message)
                return None

            password, ok = QInputDialog.getText(parent, "Password", f"{action} password:", QLineEdit.Password)
            if not ok:
                return None
            
            is_valid, message = self.validate_password(password)
            if is_valid:
                self.attempts = 0
                return password
            else:
                self.attempts += 1
                self.last_attempt_time = time.time()
                QMessageBox.warning(parent, "Invalid Password", message)
                if self.attempts >= self.max_attempts:
                    QMessageBox.warning(parent, "Account Locked", f"Too many incorrect attempts. Please try again in {self.lockout_time} seconds.")
                    return None

    def change_password(self, parent=None):
        old_password = self.prompt_for_password(parent, is_new=False)
        if old_password is None:
            return None, "Password change cancelled."

        new_password = self.prompt_for_password(parent, is_new=True)
        if new_password is None:
            return None, "Password change cancelled."

        confirm_password = self.prompt_for_password(parent, is_new=True)
        if confirm_password is None:
            return None, "Password change cancelled."

        if new_password != confirm_password:
            QMessageBox.warning(parent, "Password Mismatch", "New passwords do not match.")
            return None, "New passwords do not match."

        return new_password, "Password changed successfully."

# Example usage
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    
    password_manager = PasswordManager()
    
    # Prompt for initial password
    initial_password = password_manager.prompt_for_password()
    if initial_password:
        print("Initial password set successfully.")
    
    # Change password
    new_password, message = password_manager.change_password()
    print(message)

    sys.exit(app.exec_())
