import time
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
from threading import Thread, Event

class OLEDButtonController(Thread):
    def __init__(self, button_pin=17):
        super().__init__()
        self.button_pin = button_pin
        self.running = True
        self.mode_index = 0
        self.modes = ["ON", "AUTO", "OFF"]
        self.display_timeout = 2  # seconds to keep display on
        self.display_until = 0    # timestamp for display timeout
        self.mode_changed = Event()
        
        # Load the heart icon
        try:
            self.icon_auto = Image.open("logo1.png").convert("1")
            self.icon_on = Image.open("logo2.png").convert("1")
        except Exception as e:
            print(f"Error loading icon: {e}")
            self.icon_auto = None
            self.icon_on = None
        
        # --- Button setup ---
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # --- OLED setup ---
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.oled = adafruit_ssd1306.SSD1306_I2C(128, 64, self.i2c)
        
        # Use even smaller font for text
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 8)
        except:
            self.font = ImageFont.load_default()

    def show_status(self):
        image = Image.new("1", (self.oled.width, self.oled.height))
        draw = ImageDraw.Draw(image)
        
        # Calculate text dimensions
        text = f"Mode: {self.modes[self.mode_index]}"
        bbox = self.font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        
        # Position text at top center
        text_x = (self.oled.width - text_width) // 2
        text_y = 2  # Small padding from top
        
        # Draw text at top
        draw.text((text_x, text_y), text, font=self.font, fill=255)
        
        # If icon loaded successfully, center it in the remaining space
        if self.icon_auto and self.mode_index == 1:
            icon_x = (self.oled.width - self.icon_auto.width) // 2
            icon_y = (self.oled.height - self.icon_auto.height) // 2
            image.paste(self.icon_auto, (icon_x, icon_y))
        elif self.icon_on and self.mode_index == 0:
            icon_x = (self.oled.width - self.icon_on.width) // 2
            icon_y = (self.oled.height - self.icon_on.height) // 2
            image.paste(self.icon_on, (icon_x, icon_y))
        
        self.oled.image(image)
        self.oled.show()
        self.display_until = time.time() + self.display_timeout
        self.mode_changed.set()

    def clear_screen(self):
        self.oled.fill(0)
        self.oled.show()

    def stop(self):
        self.running = False
        self.clear_screen()
        GPIO.cleanup()

    def run(self):
        print("OLED Button Controller started...")
        try:
            while self.running:
                current_time = time.time()
                
                # Handle button press
                if GPIO.input(self.button_pin) == GPIO.LOW:
                    # Wait for button release (debounce)
                    time.sleep(0.05)
                    while GPIO.input(self.button_pin) == GPIO.LOW and self.running:
                        time.sleep(0.01)
                    
                    # Change mode and show status
                    self.mode_index = (self.mode_index + 1) % len(self.modes)
                    self.show_status()
                    self.mode_changed.set()
                
                # Clear display if timeout reached
                if current_time > self.display_until:
                    self.clear_screen()
                
                time.sleep(0.05)
                
        except Exception as e:
            print(f"Error in OLED Button Controller: {e}")
            self.stop()

if __name__ == "__main__":

    controller = OLEDButtonController()
    controller.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        controller.stop()