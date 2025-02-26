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

        self.text_lines = {1: "", 2: "", 3: ""}  # Stores text for each line
        self.scroll_offsets = {1: 0, 2: 0, 3: 0}  # Scroll positions per line
        self.running = True  # Controls the display loop
        self.lock = threading.Lock()

        # Start the display update loop in a background thread
        self.thread = threading.Thread(target=self._update_display, daemon=True)
        self.thread.start()

    def _update_display(self):
        """Background loop that updates the display continuously without flickering."""
        while self.running:
            with self.lock:
                with canvas(self.device) as draw:
                    for line, text in self.text_lines.items():
                        y_position = (line - 1) * 20

                        if text:
                            text_width, _ = self.font.getsize(text)

                            # If text fits within screen, display statically
                            if text_width <= 128:
                                draw.text((10, y_position), text, font=self.font, fill="white")
                                self.scroll_offsets[line] = 0  # Reset scrolling
                            else:
                                # Scroll text if too long
                                x_position = -self.scroll_offsets[line] + 10
                                draw.text((x_position, y_position), text, font=self.font, fill="white")
                                
                                # Move text left for scrolling effect
                                self.scroll_offsets[line] += 2
                                
                                # Reset scroll position when the text fully moves off-screen
                                if self.scroll_offsets[line] > text_width + 10:
                                    self.scroll_offsets[line] = 0
            
            time.sleep(0.05)  # Refresh rate for smooth scrolling

    def display_text(self, message, line=1):
        """
        Display a message on a specified line (1-3). Text scrolls if too long.

        :param message: The text to display
        :param line: Line number (1-3)
        """
        if line < 1 or line > 3:
            raise ValueError("Line number must be between 1 and 3.")

        with self.lock:
            self.text_lines[line] = message  # Update text for the given line
            self.scroll_offsets[line] = 0  # Reset scrolling for new text

    def stop(self):
        """Stop the display update loop and clear the screen."""
        self.running = False
        self.thread.join()
        self.clear()

    def clear(self):
        """Clear the display."""
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")
        with self.lock:
            self.text_lines = {1: "", 2: "", 3: ""}
            self.scroll_offsets = {1: 0, 2: 0, 3: 0}