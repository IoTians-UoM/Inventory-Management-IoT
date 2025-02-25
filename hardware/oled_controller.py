from luma.core.interface.serial import I2C
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont, ImageDraw, Image
import time

class OLED12864:
    def __init__(self, i2c_port=1, i2c_address=0x3C):
        """
        Initialize the 128x64 OLED display over I2C.
        """
        serial = I2C(port=i2c_port, address=i2c_address)
        self.device = ssd1306(serial, width=128, height=64)
        self.clear()

    def clear(self):
        """
        Clear the display.
        """
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")

    def display_message(self, message, line=1):
        """
        Display a message on a specified line (1-4) of the OLED.
        """
        if line < 1 or line > 4:
            raise ValueError("Line number must be between 1 and 4.")

        line_height = 16  # Assuming 16px per line for a 128x64 display
        y_position = (line - 1) * line_height

        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")
            draw.text((0, y_position), message, fill="white")

    def display_image(self, image_path):
        """
        Display an image on the OLED display.
        """
        image = Image.open(image_path).resize((128, 64)).convert("1")
        self.device.display(image)

    def display_custom_text(self, text_lines):
        """
        Display multiple lines of custom text.
        """
        with canvas(self.device) as draw:
            for i, line_text in enumerate(text_lines):
                if i >= 4:
                    break  # OLED 128x64 typically supports 4 lines of text
                draw.text((0, i * 16), line_text, fill="white")

    def cleanup(self):
        """
        Clear and release display resources.
        """
        self.clear()
        print("OLED cleanup done.")

