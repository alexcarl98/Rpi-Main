import pyaudio
import threading
import queue
import time
import wave
import os
import requests
import shutil
from datetime import datetime
from util import is_connected
from oled_button import OLEDButtonController
from speech_det import detect_speech
from worn_det import WearableDetector
# TODO: 
# - Improve responsiveness in turning on/off recording
# - Add a "silence" detection to turn off recording when there is no speech

# Define audio parameters
DEBUG=True
FORMAT = pyaudio.paInt16  # 16-bit audio
CHANNELS = 2  # Mono audio
RATE = 48000 # Sample rate (44.1 kHz)
CHUNK = 1024  # Number of frames per buffer
RECORD_SECONDS = 40  # Duration of each recording segment
OUTPUT_DIR = "data"

class SafeQueue:
    def __init__(self):
        self.queue = queue.Queue()

    def push(self, value):
        self.queue.put(value)

    def pop(self, timeout=None):
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def empty(self):
        return self.queue.empty()

audio_queue = SafeQueue()

class SharedState:
    def __init__(self):
        self.lock = threading.Lock()
        self.should_record = True

shared_state = SharedState()

def record_audio(stream, chunk_size, shared_state):
    while True:
        with shared_state.lock:
            if not shared_state.should_record:
                time.sleep(0.1)
                continue
        try:
            data = stream.read(chunk_size, exception_on_overflow=False)
            audio_queue.push(data)
        except Exception as e:
            print(f"Error reading audio stream: {e}")
            time.sleep(0.1)

def save_audio(frames, audio):
    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Generate a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(OUTPUT_DIR, f"{timestamp}.wav")

    # Save the recording to a WAV file
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    print(f"Audio saved as {filename}")


def load_env_file(file_path):
    env_dict = {}
    
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):  # Ignore empty lines and comments
                continue
            if '=' in line:
                key, value = line.split('=', 1)  # Split at first '=' only
                env_dict[key.strip()] = value.strip()
    return env_dict

def send_audio(file_path, supabase_url, supabase_api_key, debug=DEBUG):
    sent_dir = "sent"
    if not os.path.exists(sent_dir):
        os.makedirs(sent_dir, exist_ok=True)

    if not detect_speech(file_path):
        print(f"No speech detected, discarding: {file_path}")
        os.remove(file_path)
        return

    with open(file_path, "rb") as audio_file:
        files = {"file": (os.path.basename(file_path), audio_file, "audio/wav")}
        headers = {
            "Authorization": f"Bearer {supabase_api_key}"
        }
        if debug:
            print(f"Debug mode: Moving {file_path} to {sent_dir}")
            print(headers)
            dest_path = os.path.join(sent_dir, os.path.basename(file_path))
            shutil.move(file_path, dest_path)
            print(f"File successfully moved to: {dest_path}")
        else:
            print(f"Sending {file_path} to {supabase_url}")
            response = requests.post(supabase_url, files=files, headers=headers)
            print(f"Sent {file_path}: {response.status_code} - {response.text}")

def monitor_and_send():
    env_vars = load_env_file('.env')
    SUPABASE_FUNCTION_URL = env_vars['SUPABASE_URL']
    SUPABASE_API_KEY = env_vars['SUPABASE_API_KEY']

    while True:
        files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.wav')])
        for filename in files:
            file_path = os.path.join(OUTPUT_DIR, filename)
            if not is_connected():
                if DEBUG:
                    print("Not connected to the internet, skipping upload")
                continue
            send_audio(file_path, SUPABASE_FUNCTION_URL, SUPABASE_API_KEY)
            if not DEBUG:
                os.remove(file_path)
        time.sleep(10)

def main():
    # Initialize PortAudio
    audio = pyaudio.PyAudio()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    detector = WearableDetector()
    detection_active = False

    # Start OLED button controller thread
    oled_controller = OLEDButtonController()
    oled_controller.start()

    # Open a new audio stream
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=2,
                        frames_per_buffer=CHUNK)

    print("Recording...")

    recording_thread = threading.Thread(target=record_audio, 
                                        args=(stream, CHUNK, shared_state))
    monitoring_thread = threading.Thread(target=monitor_and_send)
    
    recording_thread.start()
    monitoring_thread.start()
    possible_modes= ['ON', 'AUTO', 'OFF']
    mode_idx = 0

    try:
        while True:
            # Update shared_state.should_record based on OLED mode
            with shared_state.lock:
                
                # shared_state.should_record = (oled_controller.mode_index != 2)  # Only record if not OFF
                mode_idx = oled_controller.mode_index
                if mode_idx==0:
                    # the device is in the ON mode, 
                    shared_state.should_record = True
                    # for now, I'll keep the detection going throughout modes 0 and 1
                    if not detection_active:
                        detection_active = True
                        detector.start()
                elif mode_idx==1:
                    # the device is in the AUTO mode, 
                    is_being_worn = detector.bool_status
                    shared_state.should_record = is_being_worn
                    if not detection_active:
                        detection_active = True
                        detector.start()
                elif mode_idx==2:
                    # the device is in the OFF mode, 
                    shared_state.should_record = False
                    if detection_active:
                        detection_active = False
                        detector.stop()

            if not shared_state.should_record:
                print("sleeping, not recording data")
                print(f"Mode: {possible_modes[mode_idx]}")
                time.sleep(5)
                continue

            frames = []
            for _ in range(int(RATE / CHUNK * RECORD_SECONDS)):
                data = audio_queue.pop(timeout=5)
                if data is not None:
                    frames.append(data)
                else:
                    print("Warning: No audio data received!")
                    break

            save_audio(frames, audio)

    except KeyboardInterrupt:
        print("Recording stopped by user.")

    finally:
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()
        # Stop the OLED controller thread
        oled_controller.stop()
        oled_controller.join()  # Wait for the thread to finish

if __name__ == "__main__":
    main()
