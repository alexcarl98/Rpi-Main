import time
import board
import busio
import numpy as np
from adafruit_mpu6050 import MPU6050
from collections import deque
import threading

class WearableDetector:
    STATUS_DICT = {
        "AMBIENT MOTION (Motion, but Cold)": False,
        "NOT WORN": False,
        "RECENTLY REMOVED (Cooling)": False,
        "WORN (Moving + Warm)": True,
        "POSSIBLY WORN (Warming Up + Motion)": True,
    }
    
    # Default parameters
    SAMPLE_RATE_HZ = 20         # Hz
    WINDOW_SIZE = 3             # Seconds
    ACC_STD_THRESHOLD = 0.05    # m/s^2
    GYRO_STD_THRESHOLD = 0.2    # deg/sec
    TEMP_BUFFER_SIZE = 6        # 6 entries → 3 minutes if sampled every 30 sec
    
    def __init__(self):
        self._status_lock = threading.Lock()
        self._temp_lock = threading.Lock()
        self._mpu_lock = threading.Lock()
        self._running = False
        self._thread = None
        
        # Protected variables
        self._current_status = "NOT WORN"
        self._temp_history = deque(maxlen=self.TEMP_BUFFER_SIZE)
        
        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self._mpu = MPU6050(i2c)
        except Exception as e:
            print(f"Error initializing MPU6050: {e}")
            raise

    def start(self):
        """Start the wear detection in a separate thread"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run_detection)
            self._thread.daemon = True
            self._thread.start()

    def stop(self):
        """Stop the wear detection thread"""
        self._running = False
        if self._thread:
            self._thread.join()
            self._thread = None

    def _run_detection(self):
        """Main detection loop running in separate thread"""
        while self._running:
            try:
                new_status = self.get_wear_status()
                with self._status_lock:
                    self._current_status = new_status
                print(f"Status: {new_status}")
                time.sleep(30)
            except Exception as e:
                print(f"Error in wear detection: {e}")
                time.sleep(5)  # Wait before retrying

    def collect_window(self):
        """Thread-safe collection of sensor data"""
        num_samples = self.WINDOW_SIZE * self.SAMPLE_RATE_HZ
        accel_data = []
        gyro_data = []
        
        for _ in range(num_samples):
            with self._mpu_lock:
                try:
                    accel = self._mpu.acceleration
                    gyro = self._mpu.gyro
                    accel_data.append(accel)
                    gyro_data.append(gyro)
                except Exception as e:
                    print(f"Error reading sensor: {e}")
                    continue
            time.sleep(1.0 / self.SAMPLE_RATE_HZ)
            
        return np.array(accel_data), np.array(gyro_data)

    def analyze_motion(self, accel_data, gyro_data):
        accel_magnitude = np.linalg.norm(accel_data, axis=1)
        accel_std = np.std(accel_magnitude)

        gyro_magnitude = np.linalg.norm(gyro_data, axis=1)
        gyro_std = np.std(gyro_magnitude)

        print(f"[DEBUG] accel_std={accel_std:.5f} m/s², gyro_std={gyro_std:.5f} rad/s")
        return (accel_std > self.ACC_STD_THRESHOLD) or (gyro_std > self.GYRO_STD_THRESHOLD)

    def record_temperature(self, temp_celsius):
        """Thread-safe temperature recording"""
        with self._temp_lock:
            self._temp_history.append((time.time(), temp_celsius))

    def get_temp_slope(self):
        """Thread-safe temperature slope calculation"""
        with self._temp_lock:
            if len(self._temp_history) < 2:
                return 0.0

            t0, temp0 = self._temp_history[0]
            t1, temp1 = self._temp_history[-1]

            delta_t = (t1 - t0) / 60.0  # convert to minutes
            delta_temp = temp1 - temp0

            return 0.0 if delta_t == 0 else delta_temp / delta_t

    @property
    def current_status(self):
        """Thread-safe status access"""
        with self._status_lock:
            return self._current_status

    @property
    def bool_status(self):
        """Thread-safe boolean status access"""
        with self._status_lock:
            return self.STATUS_DICT[self._current_status]

    @staticmethod
    def is_temp_consistent_with_skin(temp_celsius):
        return temp_celsius > 27.5

    def get_wear_status(self):
        """Determine wear status based on motion and temperature"""
        try:
            accel_data, gyro_data = self.collect_window()
            with self._mpu_lock:
                temp = self._mpu.temperature
            
            self.record_temperature(temp)
            temp_slope = self.get_temp_slope()
            moving = self.analyze_motion(accel_data, gyro_data)
            warm = self.is_temp_consistent_with_skin(temp)

            print(f"[DEBUG] Temp: {temp:.2f}°C, ΔT/Δt: {temp_slope:.3f} °C/min")

            if moving:
                if warm:
                    return "WORN (Moving + Warm)"
                elif temp_slope > 0.1:
                    return "POSSIBLY WORN (Warming Up + Motion)"
                else:
                    return "AMBIENT MOTION (Motion, but Cold)"
            else:
                if temp_slope < -0.1:
                    return "RECENTLY REMOVED (Cooling)"
                else:
                    return "NOT WORN"
                    
        except Exception as e:
            print(f"Error in wear status determination: {e}")
            return self.current_status  # Return last known status on error

def main():
    detector = WearableDetector()
    print("Starting Wear Detection...")
    print("Commands: 'q' to quit, 's' to start/stop detection")
    detection_active = False
    
    try:
        while True:
            cmd = input().lower()
            if cmd == 'q':
                if detection_active:
                    detector.stop()
                print("\nExiting...")
                break
            elif cmd == 's':
                if detection_active:
                    detector.stop()
                    detection_active = False
                    print("Detection stopped")
                else:
                    detector.start()
                    detection_active = True
                    print("Detection started")
            else:
                print("Unknown command. Use 'q' to quit or 's' to start/stop")
    except KeyboardInterrupt:
        if detection_active:
            detector.stop()
        print("\nExiting...")

if __name__ == "__main__":
    main()
