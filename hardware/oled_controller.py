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
        self.clear()

    def clear(self):
        """Clear the display."""
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")

    def display_text(self, message, line=1, scroll_speed=0.05):
        """
        Display a message on a specified line (1-3). Scrolls if the text is too long.
        
        :param message: The text to display
        :param line: Line number (1-3)
        :param scroll_speed: Speed of scrolling (lower = faster)
        """
        if line < 1 or line > 3:
            raise ValueError("Line number must be between 1 and 3.")

        line_height = 20  # Adjusted for larger font
        y_position = (line - 1) * line_height

        # Get text width
        text_width, _ = self.font.getsize(message)

        # If text fits, just display it statically
        if text_width <= 128:
            with canvas(self.device) as draw:
                draw.text((10, y_position), message, font=self.font, fill="white")
            return

        # Scrolling effect
        for offset in range(text_width + 128):  # Move text across screen
            with canvas(self.device) as draw:
                draw.text((-offset + 10, y_position), message, font=self.font, fill="white")
            time.sleep(scroll_speed)  # Adjust scroll speed

    def display_custom_text(self, text_lines):
        """Display multiple lines of custom text (without scrolling)."""
        with canvas(self.device) as draw:
            for i, line_text in enumerate(text_lines):
                if i >= 3:  # Limit to 3 lines to avoid overlap
                    break  
                y_position = i * 20
                draw.text((10, y_position), line_text, font=self.font, fill="white")

    def cleanup(self):
        """Clear and release display resources."""
        self.clear()
        print("OLED cleanup done.")