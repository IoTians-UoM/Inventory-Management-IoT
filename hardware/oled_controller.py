import time
import threading
import queue
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas
from PIL import ImageFont, ImageDraw

class OLEDController:
    def __init__(self, i2c_port=1, i2c_address=0x3C, font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size=16):
        """
        Initialize the 128x64 OLED display with independent scrolling and a message queue.
        """
        serial = i2c(port=i2c_port, address=i2c_address)
        self.device = ssd1306(serial, width=128, height=64)
        self.font = ImageFont.truetype(font_path, font_size)

        self.text_queue = queue.Queue()  # Queue to handle display messages
        self.text_lines = {1: "", 2: "", 3: ""}  # Store text per line
        self.scroll_offsets = {1: 0, 2: 0, 3: 0}  # Track scrolling position
        self.scroll_enabled = {1: False, 2: False, 3: False}  # Scrolling status
        self.running = True  # Controls display loop
        self.lock = threading.Lock()

        # Start the display update loop in a separate thread
        self.display_thread = threading.Thread(target=self._update_display, daemon=True)
        self.display_thread.start()

        # Start the message processing thread
        self.message_thread = threading.Thread(target=self._process_messages, daemon=True)
        self.message_thread.start()

    def _update_display(self):
        """Continuously updates the display to show text and handle scrolling."""
        while self.running:
            with self.lock:
                with canvas(self.device) as draw:
                    for line, text in self.text_lines.items():
                        y_position = (line - 1) * 20

                        if not isinstance(text, str):  # Ensure text is a valid string
                            text = ""

                        text_width, _ = self.font.getsize(text)  # Safe to call now

                        if text_width <= 120:
                            # Static text (fits on screen)
                            draw.text((10, y_position), text, font=self.font, fill="white")
                            self.scroll_offsets[line] = 0
                            self.scroll_enabled[line] = False
                        else:
                            # Scrolling text (too long for screen)
                            self.scroll_enabled[line] = True
                            x_position = -self.scroll_offsets[line] + 10
                            draw.text((x_position, y_position), text, font=self.font, fill="white")

                            # Move text left for scrolling effect
                            self.scroll_offsets[line] += 2

                            # Reset scroll position when text fully moves off-screen
                            if self.scroll_offsets[line] > text_width + 10:
                                self.scroll_offsets[line] = 0

            time.sleep(0.05)  # Smooth refresh rate


    def _process_messages(self):
        """Thread that processes the display queue and updates text on the OLED."""
        while self.running:
            try:
                line, message = self.text_queue.get(timeout=1)  # Get message from queue (timeout prevents blocking)
                with self.lock:
                    self.text_lines[line] = message  # Update text for the given line
                    self.scroll_offsets[line] = 0  # Reset scrolling position
                    self.scroll_enabled[line] = True  # Enable scrolling if needed
                self.text_queue.task_done()
            except queue.Empty:
                continue  # If no messages, continue checking

    def display_text(self, message, line=1):
        """
        Queue a message to display on the OLED at a specific line.

        :param message: Text to display.
        :param line: Line number (1-3).
        """
        if line < 1 or line > 3:
            raise ValueError("Line number must be between 1 and 3.")

        if not isinstance(message, str):
            message = str(message)  # Convert to string if needed

        self.text_queue.put((line, message))  # Add message to queue


    def stop(self):
        """Stop the display update loop and clear the screen."""
        self.running = False
        self.display_thread.join()
        self.message_thread.join()
        self.clear()

    def clear(self):
        """Clear the display."""
        with canvas(self.device) as draw:
            draw.rectangle(self.device.bounding_box, outline="black", fill="black")
        with self.lock:
            self.text_lines = {1: "", 2: "", 3: ""}
            self.scroll_offsets = {1: 0, 2: 0, 3: 0}
            self.scroll_enabled = {1: False, 2: False, 3: False}