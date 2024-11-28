
class BaseIndicator:
    def __init__(self):
        pass

    def calculate(self, data):
        raise NotImplementedError("Subclass must implement abstract method")
