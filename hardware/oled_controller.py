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
        """
        Clear the display.
        """
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")

    def display_message(self, message, line=1):
        """
        Display a message on a specified line (1-3) of the OLED using a larger font.
        """
        if line < 1 or line > 3:
            raise ValueError("Line number must be between 1 and 3 for better spacing.")

        line_height = 20  # Increase line spacing for larger font
        y_position = (line - 1) * line_height

        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")
            draw.text((10, y_position), message, font=self.font, fill="white")  # Centered text

    def display_custom_text(self, text_lines):
        """
        Display multiple lines of custom text with larger font.
        """
        with canvas(self.device) as draw:
            for i, line_text in enumerate(text_lines):
                if i >= 3:  # Limit to 3 lines to avoid text overlap
                    break  
                y_position = i * 20
                draw.text((10, y_position), line_text, font=self.font, fill="white")  # Adjusted for larger font

    def cleanup(self):
        """
        Clear and release display resources.
        """
        self.clear()
        print("OLED cleanup done.")
