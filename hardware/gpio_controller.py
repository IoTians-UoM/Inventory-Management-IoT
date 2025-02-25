import RPi.GPIO as GPIO

class GPIOHandler:
    def __init__(self, pin, mode="in", pull="up"):
        """
        Initialize the GPIOHandler.
        
        Parameters:
          pin (int): The BCM GPIO pin number.
          mode (str or int): "in" or "out" as a string (case-insensitive), or GPIO.IN/GPIO.OUT.
          pull (str): For input mode, specify "up", "down", or "none" (case-insensitive). Ignored for output mode.
        """
        self.pin = pin
        
        # Allow mode to be passed as a string or a GPIO constant.
        if isinstance(mode, str):
            mode_lower = mode.lower()
            if mode_lower == "in":
                self.mode = GPIO.IN
            elif mode_lower == "out":
                self.mode = GPIO.OUT
            else:
                raise ValueError("Invalid mode string. Use 'in' or 'out'.")
        else:
            self.mode = mode  # Assume it's already GPIO.IN or GPIO.OUT
        
        GPIO.setmode(GPIO.BCM)
        
        if self.mode == GPIO.IN:
            # Process the pull resistor setting.
            if isinstance(pull, str):
                pull_lower = pull.lower()
                if pull_lower == "up":
                    pull_setting = GPIO.PUD_UP
                elif pull_lower == "down":
                    pull_setting = GPIO.PUD_DOWN
                elif pull_lower == "none":
                    pull_setting = GPIO.PUD_OFF
                else:
                    raise ValueError("Invalid pull value. Choose 'up', 'down', or 'none'.")
            else:
                pull_setting = pull  # If not a string, assume valid constant.
            
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=pull_setting)
        elif self.mode == GPIO.OUT:
            GPIO.setup(self.pin, GPIO.OUT)
        else:
            raise ValueError("Invalid mode. Use 'in' or 'out' (or GPIO.IN/GPIO.OUT).")

    def start_interrupt(self, edge=GPIO.FALLING, callback=None, bouncetime=300):
        """
        Set up edge detection for the pin. Only available for input mode.

        Parameters:
          edge: GPIO.FALLING, GPIO.RISING, or GPIO.BOTH. Default is GPIO.FALLING.
          callback: The function to call when the edge is detected.
          bouncetime (int): Time in milliseconds to debounce. Default is 300.
        """
        if self.mode != GPIO.IN:
            raise RuntimeError("Interrupts can only be set on pins configured as input.")
        if callback is None:
            raise ValueError("A callback function must be provided.")
        GPIO.add_event_detect(self.pin, edge, callback=callback, bouncetime=bouncetime)

    def read(self):
        """
        Read the current value of the pin. Only available for input mode.
        """
        if self.mode != GPIO.IN:
            raise RuntimeError("Read is only available on input mode.")
        return GPIO.input(self.pin)

    def write(self, value):
        """
        Write a value to the pin. Only available for output mode.

        Parameters:
          value: True/False or GPIO.HIGH/GPIO.LOW.
        """
        if self.mode != GPIO.OUT:
            raise RuntimeError("Write is only available on output mode.")
        GPIO.output(self.pin, value)

    def cleanup(self):
        """
        Clean up the GPIO settings for this pin.
        """
        GPIO.cleanup(self.pin)