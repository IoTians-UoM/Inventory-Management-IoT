import time
import threading
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont, ImageDraw, Image

class OLEDController:
    def __init__(self, i2c_port=1, i2c_address=0x3C, font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size=16):
        """
        Initialize the 128x64 OLED display over I2C with larger font support.
        """
        serial = i2c(port=i2c_port, address=i2c_address)
        self.device = ssd1306(serial, width=128, height=64)
        self.font = ImageFont.truetype(font_path, font_size)  # Load custom font
        self.scrolling_text = {}  # Store text scrolling states
        self.scroll_threads = {}  # Track threads for scrolling
        self.lock = threading.Lock()
        self.clear()

    def clear(self):
        """Clear the display."""
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")

    def _scroll_text(self, message, line, scroll_speed):
        """Handles independent scrolling for each line."""
        text_width, _ = self.font.getsize(message)
        line_height = 20
        y_position = (line - 1) * line_height

        while self.scrolling_text.get(line, False):
            for offset in range(text_width + 128):  # Move text across screen
                if not self.scrolling_text.get(line, False):  # Stop if interrupted
                    return
                
                with self.lock:
                    with canvas(self.device) as draw:
                        for l, text in self.scrolling_text.items():
                            y_pos = (l - 1) * line_height
                            if l == line:
                                draw.text((-offset + 10, y_position), message, font=self.font, fill="white")
                            else:
                                draw.text((10, y_pos), text, font=self.font, fill="white")

                time.sleep(scroll_speed)  # Adjust scroll speed

    def display_text(self, message, line=1, scroll_speed=0.05):
        """
        Display a message on a specified line (1-3) independently scrolling if needed.

        :param message: The text to display
        :param line: Line number (1-3)
        :param scroll_speed: Speed of scrolling (lower = faster)
        """
        if line < 1 or line > 3:
            raise ValueError("Line number must be between 1 and 3.")

        text_width, _ = self.font.getsize(message)
        self.scrolling_text[line] = message  # Store message for this line

        # If text fits, display statically
        if text_width <= 128:
            with canvas(self.device) as draw:
                for l, text in self.scrolling_text.items():
                    y_position = (l - 1) * 20
                    draw.text((10, y_position), text, font=self.font, fill="white")
            return

        # Stop existing thread for this line if running
        if line in self.scroll_threads and self.scroll_threads[line].is_alive():
            self.scrolling_text[line] = False
            self.scroll_threads[line].join()

        # Start a new scrolling thread for this line
        self.scrolling_text[line] = True
        self.scroll_threads[line] = threading.Thread(target=self._scroll_text, args=(message, line, scroll_speed), daemon=True)
        self.scroll_threads[line].start()

    def stop_scrolling(self, line=None):
        """Stop scrolling on a specific line or all lines."""
        if line:
            self.scrolling_text[line] = False
            if line in self.scroll_threads and self.scroll_threads[line].is_alive():
                self.scroll_threads[line].join()
        else:
            for l in self.scrolling_text.keys():
                self.scrolling_text[l] = False

    def display_custom_text(self, text_lines):
        """Display multiple lines of custom text (without scrolling)."""
        self.stop_scrolling()  # Stop all scrolling before displaying static text
        with canvas(self.device) as draw:
            for i, line_text in enumerate(text_lines):
                if i >= 3:  # Limit to 3 lines to avoid overlap
                    break
                y_position = i * 20
                draw.text((10, y_position), line_text, font=self.font, fill="white")

    def cleanup(self):
        """Clear and release display resources."""
        self.stop_scrolling()
        self.clear()
        print("OLED cleanup done.")
