from abc import ABC, abstractmethod

class AbstractBulb(ABC):
    @abstractmethod
    def __init__(self, config):
        pass

    @abstractmethod
    def set_temp(self, temp_percent):
        pass

    @abstractmethod
    def set_rgb(self, r, g, b):
        pass

    @abstractmethod
    def set_brightness(self, brightness):
        pass

    @abstractmethod
    def set_power(self, on):
        pass