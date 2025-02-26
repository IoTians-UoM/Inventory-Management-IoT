import time
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
        self.text_buffer = ["", "", ""]  # Stores current text for each line
        self.offsets = [0, 0, 0]  # Stores scrolling positions
        self.clear()

    def clear(self):
        """Clear the display and reset text buffer."""
        self.text_buffer = ["", "", ""]
        self.offsets = [0, 0, 0]
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")

    def display_text(self, message, line=1, scroll_speed=0.01):
        """
        Display a message on a specific line without clearing other lines.
        Scrolls if the text is too long.

        :param message: The text to display
        :param line: Line number (1-3)
        """
        if line < 1 or line > 3:
            raise ValueError("Line number must be between 1 and 3.")

        index = line - 1  # Convert to 0-based index
        self.text_buffer[index] = message  # Store message in buffer
        self.offsets[index] = 0  # Reset scrolling position

        # Start scrolling process
        self._start_scrolling(scroll_speed=scroll_speed)

    def _start_scrolling(self, scroll_speed):
        """
        Internal function to handle scrolling for all lines.
        """
        line_heights = [0, 20, 40]  # Y positions for 3 lines
        text_widths = [self.font.getsize(text)[0] for text in self.text_buffer]
        need_scroll = [width > 128 for width in text_widths]  # Check if scrolling is needed

        while any(need_scroll):  # Continue scrolling while any text is too long
            with canvas(self.device) as draw:
                for i in range(3):
                    if not self.text_buffer[i]:  # Skip empty lines
                        continue

                    x_position = -self.offsets[i] + 10  # Adjust scrolling position
                    draw.text((x_position, line_heights[i]), self.text_buffer[i], font=self.font, fill="white")

                    # Scroll only if text is too long
                    if need_scroll[i]:
                        self.offsets[i] += 2  # Move text left
                        if self.offsets[i] > text_widths[i]:  # Reset when fully scrolled
                            self.offsets[i] = -128

            time.sleep(scroll_speed)  # Adjust scroll speed

    def cleanup(self):
        """Clear and release display resources."""
        self.clear()
        print("OLED cleanup done.")
