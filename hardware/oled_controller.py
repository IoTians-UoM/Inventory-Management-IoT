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

    def display_text(self, text_lines, scroll_speed=0.05):
        """
        Display up to 3 lines at the same time. Scrolls text if it's too long.

        :param text_lines: List of text strings (max 3 lines)
        :param scroll_speed: Speed of scrolling (lower = faster)
        """
        max_lines = 3
        text_lines = text_lines[:max_lines]  # Ensure max 3 lines
        line_heights = [0, 20, 40]  # Y positions for 3 lines
        offsets = [0] * len(text_lines)  # Starting positions for each line

        # Get text widths
        text_widths = [self.font.getsize(text)[0] for text in text_lines]

        # Determine if any line needs scrolling
        need_scroll = [width > 128 for width in text_widths]

        while any(need_scroll):  # Continue scrolling until all fit
            with canvas(self.device) as draw:
                for i, text in enumerate(text_lines):
                    x_position = -offsets[i] + 10  # Adjust scrolling position
                    draw.text((x_position, line_heights[i]), text, font=self.font, fill="white")

                    # Scroll if needed
                    if need_scroll[i]:
                        offsets[i] += 2  # Move text left
                        if offsets[i] > text_widths[i]:  # Reset when fully scrolled
                            offsets[i] = -128

            time.sleep(scroll_speed)  # Adjust scroll speed

    def cleanup(self):
        """Clear and release display resources."""
        self.clear()
        print("OLED cleanup done.")