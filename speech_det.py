import numpy as np
import wave
import time
def compute_rms(signal):
    if len(signal) == 0:
        return 0.0
    return np.sqrt(np.mean(signal.astype(np.float64)**2))

def compute_zcr(signal):
    if len(signal) == 0:
        return 0.0
    return ((signal[:-1] * signal[1:]) < 0).sum() / len(signal)

def compute_delta(signal):
    if len(signal) < 2:
        return 0.0
    return np.mean(np.abs(np.diff(signal)))

def detect_speech(filename, energy_threshold=0.0003, delta_threshold=0.00006):
    with wave.open(filename, 'rb') as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        nframes = wf.getnframes()

        print(f"Channels: {channels}, Sample Width: {sampwidth*8} bits, Rate: {framerate}, Frames: {nframes}")

        audio = wf.readframes(nframes)

        if sampwidth == 4:  # 32-bit
            audio = np.frombuffer(audio, dtype=np.int32)
            # Normalize
            audio = audio.astype(np.float64) / 2147483647.0
        elif sampwidth == 2:  # 16-bit
            audio = np.frombuffer(audio, dtype=np.int16)
            audio = audio.astype(np.float64) / 32767.0

        else:
            raise ValueError(f"Unsupported sample width: {sampwidth}")

        audio = audio.reshape(-1, channels)
        audio_left = audio[:, 0]

    frame_size = int(framerate * 0.03)  # 30 ms per frame
    num_frames = len(audio_left) // frame_size

    speech_frames = 0

    for i in range(num_frames):
        frame = audio_left[i*frame_size : (i+1)*frame_size]
        
        if len(frame) == 0:
            continue

        rms = compute_rms(frame)
        delta = compute_delta(frame)

        if rms > energy_threshold and delta > delta_threshold:
            speech_frames += 1

    if num_frames == 0:
        speech_ratio = 0.0
    else:
        speech_ratio = speech_frames / num_frames

    print(f"Speech frames ratio: {speech_ratio:.2f}")

    return speech_ratio > 0.1  # 10% frames must show speech-like activity

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python speech_det.py filename.wav")
    else:
        start_time = time.time()
        has_speech = detect_speech(sys.argv[1])
        end_time = time.time()
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print("Speech detected!" if has_speech else "No speech detected.")