import RPi.GPIO as GPIO

class GPIOHandler:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def start_interrupt(self):
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self.button_press_callback, bouncetime=300)

    def cleanup(self):
        GPIO.cleanup(self.pin)
