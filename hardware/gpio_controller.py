import RPi.GPIO as GPIO

class GPIOController:
    def __init__(self, pin, mode="in", active="low"):
        """
        Initialize the GPIOHandler.
        
        Parameters:
          pin (int): The BCM GPIO pin number.
          mode (str): "in" or "out" (case-insensitive) to configure the pin.
          active (str): For input mode, specify "high" or "low" indicating the active state.
                        For active-high, the button press sets the pin high (so use a pull-down resistor).
                        For active-low, the button press sets the pin low (so use a pull-up resistor).
        """
        self.pin = pin
        
        # Determine mode.
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
        
        # Set BCM numbering.
        GPIO.setmode(GPIO.BCM)
        
        if self.mode == GPIO.IN:
            if isinstance(active, str):
                active_lower = active.lower()
                if active_lower == "high":
                    self.active = "high"
                    pull_setting = GPIO.PUD_DOWN  # Normally low; goes high when pressed.
                elif active_lower == "low":
                    self.active = "low"
                    pull_setting = GPIO.PUD_UP    # Normally high; goes low when pressed.
                else:
                    raise ValueError("Invalid active value. Use 'high' or 'low'.")
            else:
                raise ValueError("active parameter must be a string: 'high' or 'low'.")
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=pull_setting)
        elif self.mode == GPIO.OUT:
            GPIO.setup(self.pin, GPIO.OUT)
        else:
            raise ValueError("Invalid mode. Use 'in' or 'out'.")
    
    def start_interrupt(self, edge=None, callback=None, bouncetime=300):
        """
        Set up edge detection on the pin.
        
        If the pin is not already in input mode, it will be reconfigured.
        For active-high (active="high"), the default edge is rising,
        while for active-low (active="low"), the default edge is falling.
        
        Parameters:
          edge: GPIO.FALLING, GPIO.RISING, or GPIO.BOTH. If None, a default is chosen.
          callback: The function to call when the edge is detected.
          bouncetime (int): Debounce time in milliseconds.
        """
        if self.mode != GPIO.IN:
            print(f"Warning: Pin {self.pin} is not in input mode. Cleaning up and reconfiguring to input.")
            GPIO.cleanup(self.pin)
            pull_setting = GPIO.PUD_DOWN if self.active == "high" else GPIO.PUD_UP
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=pull_setting)
            self.mode = GPIO.IN
        
        try:
            GPIO.remove_event_detect(self.pin)
        except Exception:
            pass
        
        if callback is None:
            raise ValueError("A callback function must be provided for interrupt detection.")
        
        if edge is None:
            edge = GPIO.RISING if self.active == "high" else GPIO.FALLING
        
        try:
            GPIO.add_event_detect(self.pin, edge, callback=callback, bouncetime=bouncetime)
        except Exception as e:
            raise RuntimeError(f"Failed to add edge detection on pin {self.pin}: {e}")
    
    def read(self):
        """
        Read the current value of the pin. Available only in input mode.
        """
        if self.mode != GPIO.IN:
            raise RuntimeError("Read is only available when the pin is in input mode.")
        return GPIO.input(self.pin)
    
    def write(self, value):
        """
        Write a value to the pin. Available only in output mode.
        
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
