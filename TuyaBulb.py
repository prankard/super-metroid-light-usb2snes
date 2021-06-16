from tuya_bulb_control import Bulb
from abstract_bulb import AbstractBulb

class TuyaBulb(AbstractBulb):

    bulb = None

    def __init__(self, config):
        
        self.bulb = Bulb(
            client_id=config['CLIENT_ID'],
            secret_key=config['SECRET_KEY'],
            device_id=config['DEVICE_ID'],
            region_key=config['REGION_KEY']
        )
        pass

    def set_temp(self, temp_percent):
        self.bulb.set_colour_temp_v2(temp_percent)
        pass

    def set_rgb(self, r, g, b):
        self.bulb.set_colour_v2(rgb=(r, g, b))
        pass

    def set_brightness(self, brightness):
        self.bulb.set_bright_v2(brightness)
        pass

    def set_power(self, on):
        if on:
            self.bulb.turn_on()
        else:
            self.bulb.turn_off()
        pass