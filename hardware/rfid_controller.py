import RPi.GPIO as GPIO
from mfrc522 import MFRC522, SimpleMFRC522
import time

class RFIDController:
    def __init__(self):
        self.reader = SimpleMFRC522()

    def detect_tag(self):
        try:
            print("Hold a tag near the reader")
            id, text = self.reader.read()
            print("Tag detected, ID:", id)
            return id
        except Exception as e:
            print("Error reading tag:", e)
            return None
        
    def write_data(self, block, data):
        try:
            print(f"Writing to tag: '{data}'")
            self.reader.write(data)
            print("Data written successfully.")
            return True
        except Exception as e:
            print("Error writing data:", e)
            return False
        
    def read_data(self, block):
        try:
            print("Reading tag...")
            data = self.reader.read()
            print(f"Data read from tag: '{data}'")
            return data
        except Exception as e:
            print("Error reading data:", e)
            return None
        
    def cleanup(self):
        self.reader.cleanup()
        print("Cleaned up RFID resources.")