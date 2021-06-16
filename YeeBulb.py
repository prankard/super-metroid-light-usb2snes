from abstract_bulb import AbstractBulb
from yeelight import Bulb

#bulb.set_color_temp(4700)
#bulb.set_brightness(100)
#bulb.turn_on()

class YeeBulb(AbstractBulb):

    bulb = None

    def __init__(self, config):
        self.bulb = Bulb(config['IP'])
        pass

    def set_temp(self, temp_percent):
        self.bulb.set_color_temp(temp_percent * 4800 + 1700) # 1700K to 6500K
        pass

    def set_rgb(self, r, g, b):
        self.bulb.set_rgb(r, g, b)
        pass

    def set_brightness(self, brightness):
        self.bulb.set_brightness(brightness)
        pass

    def set_power(self, on):
        if on:
            self.bulb.turn_on()
        else:
            self.bulb.turn_off()
        pass