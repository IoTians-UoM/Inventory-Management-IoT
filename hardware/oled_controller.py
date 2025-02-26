import time
import threading
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont, ImageDraw

class OLEDController:
    def __init__(self, i2c_port=1, i2c_address=0x3C, font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size=16):
        """
        Initialize the 128x64 OLED display over I2C with larger font support.
        """
        serial = i2c(port=i2c_port, address=i2c_address)
        self.device = ssd1306(serial, width=128, height=64)
        self.font = ImageFont.truetype(font_path, font_size)

        self.text_lines = {}  # Store text content for each line
        self.offsets = {}  # Store x-offsets for scrolling text
        self.running = False  # Control loop execution
        self.lock = threading.Lock()

        # Start the display update loop in a separate thread
        self.thread = threading.Thread(target=self._update_display, daemon=True)
        self.thread.start()

    def _update_display(self):
        """Continuously updates the display, scrolling text if necessary."""
        self.running = True

        while self.running:
            with self.lock:
                with canvas(self.device) as draw:
                    for line, text in self.text_lines.items():
                        y_position = (line - 1) * 20

                        if text:
                            text_width, _ = self.font.getsize(text)

                            # Initialize offset if it doesn't exist
                            if line not in self.offsets:
                                self.offsets[line] = 128  # Start scrolling from the right

                            # If text is wider than screen, scroll it
                            if text_width > 128:
                                x_position = -self.offsets[line] + 10
                                draw.text((x_position, y_position), text, font=self.font, fill="white")
                                self.offsets[line] += 2  # Adjust speed of scrolling

                                # Reset scroll position when fully off-screen
                                if self.offsets[line] > text_width + 10:
                                    self.offsets[line] = 128
                            else:
                                # If text fits, display statically
                                draw.text((10, y_position), text, font=self.font, fill="white")

            time.sleep(0.05)  # Refresh rate for smooth scrolling

    def display_text(self, message, line=1):
        """
        Display a message on a specified line (1-3). If text is too long, it scrolls.

        :param message: The text to display
        :param line: Line number (1-3)
        """
        if line < 1 or line > 3:
            raise ValueError("Line number must be between 1 and 3.")

        with self.lock:
            self.text_lines[line] = message  # Store the message

    def stop(self):
        """Stop the display loop and clear the screen."""
        self.running = False
        self.thread.join()
        self.clear()

    def clear(self):
        """Clear the display."""
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")
        self.text_lines.clear()
        self.offsets.clear()