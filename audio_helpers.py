import pyaudio

def print_audio_devices():
    audio = pyaudio.PyAudio()
    for i in range(audio.get_device_count()):
        device_info = audio.get_device_info_by_index(i)
        print(f"Device {i}: {device_info['name']}")
        print(f"  Input channels: {device_info['maxInputChannels']}")
        print(f"  Output channels: {device_info['maxOutputChannels']}")
        print(f"  Default sample rate: {device_info['defaultSampleRate']}")

# Add this call at the start of main()
print_audio_devices()