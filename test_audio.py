import argparse
import subprocess
import os

def record_audio(filename="test.wav", duration=5, sample_rate=48000):
    cmd = [
        "arecord",
        "-D", "hw:1,0",
        "-f", "S32_LE",
        "-c", "2",
        "-r", str(sample_rate),
        "-d", str(duration),
        filename
    ]
    print("Recording...")
    subprocess.run(cmd)
    print(f"Saved recording to {filename}")
    print("Done!")

if __name__ == "__main__":
    record_audio()
