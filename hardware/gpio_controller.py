import RPi.GPIO as GPIO

class GPIOController:
    def __init__(self, pin, mode="in", pull="up"):
        """
        Initialize the GPIOHandler.
        
        Parameters:
          pin (int): The BCM GPIO pin number.
          mode (str): "in" or "out" (case-insensitive) to configure the pin.
          pull (str): For input mode, specify "up", "down", or "none" (case-insensitive). Ignored in output mode.
        """
        self.pin = pin
        
        # Set the mode using strings ("in"/"out") or direct GPIO constants.
        if isinstance(mode, str):
            mode_lower = mode.lower()
            if mode_lower == "in":
                self.mode = GPIO.IN
            elif mode_lower == "out":
                self.mode = GPIO.OUT
            else:
                raise ValueError("Invalid mode string. Use 'in' or 'out'.")
        else:
            self.mode = mode
        
        # Initialize GPIO using BCM numbering.
        GPIO.setmode(GPIO.BCM)
        
        if self.mode == GPIO.IN:
            # Determine the pull resistor setting.
            if isinstance(pull, str):
                pull_lower = pull.lower()
                if pull_lower == "up":
                    pull_setting = GPIO.PUD_UP
                elif pull_lower == "down":
                    pull_setting = GPIO.PUD_DOWN
                elif pull_lower == "none":
                    pull_setting = GPIO.PUD_OFF
                else:
                    raise ValueError("Invalid pull value. Use 'up', 'down', or 'none'.")
            else:
                pull_setting = pull
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=pull_setting)
        elif self.mode == GPIO.OUT:
            GPIO.setup(self.pin, GPIO.OUT)
        else:
            raise ValueError("Invalid mode. Use 'in' or 'out'.")
    
    def start_interrupt(self, edge=GPIO.FALLING, callback=None, bouncetime=300):
        """
        Set up edge detection for the pin.
        If the pin is not currently in input mode, reconfigure it as input (with a default pull-up).
        
        Parameters:
          edge: GPIO.FALLING, GPIO.RISING, or GPIO.BOTH.
          callback: The function to be called when the edge is detected.
          bouncetime (int): Time in milliseconds to debounce. Default is 300.
        """
        # If the pin isn't set as input, reconfigure it.
        if self.mode != GPIO.IN:
            print(f"Warning: Pin {self.pin} is not in input mode. Reconfiguring to input for interrupt detection.")
            self.mode = GPIO.IN
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Remove any previous event detection on this pin.
        try:
            GPIO.remove_event_detect(self.pin)
        except RuntimeError:
            # This may occur if no event detection was previously set.
            pass
        
        if callback is None:
            raise ValueError("A callback function must be provided for interrupt detection.")
        
        try:
            GPIO.add_event_detect(self.pin, edge, callback=callback, bouncetime=bouncetime)
        except Exception as e:
            raise RuntimeError(f"Failed to add edge detection on pin {self.pin}: {e}")
    
    def read(self):
        """
        Read the current value of the pin. Only available in input mode.
        """
        if self.mode != GPIO.IN:
            raise RuntimeError("Read is only available when the pin is in input mode.")
        return GPIO.input(self.pin)
    
    def write(self, value):
        """
        Write a value to the pin. Only available in output mode.
        
        Parameters:
          value: True/False or GPIO.HIGH/GPIO.LOW.
        """
        if self.mode != GPIO.OUT:
            raise RuntimeError("Write is only available when the pin is in output mode.")
        GPIO.output(self.pin, value)
    
    def cleanup(self):
        """
        Clean up the GPIO settings for this pin.
        """
        GPIO.cleanup(self.pin)
        print(f"Cleaned up GPIO pin {self.pin}.")
