import numpy as np
import zmq
import time
import collections
from collections import deque
from pylsl import StreamInlet, resolve_streams
from scipy.signal import welch, iirnotch, filtfilt, butter
from pylsl import StreamInlet, resolve_streams
import time


ma_window = deque(maxlen=64)   # 8 samples ≈ 2 s at 4 Hz updates


context = zmq.Context()
pub = context.socket(zmq.PUB)
pub.bind("tcp://127.0.0.1:5556")   # local PUB endpoint

print("Looking for an EEG stream...")

# Keep trying for up to 10 seconds
start_time = time.time()
streams = []

while not streams and time.time() - start_time < 10:
    streams = resolve_streams()
    streams = [s for s in streams if s.type() == 'EEG']
    time.sleep(0.5)

if not streams:
    print("No EEG stream found. Make sure Muse is streaming via muselsl.")
    exit(1)

inlet = StreamInlet(streams[0])
print("EEG stream found.")


# Sampling rate (Muse sends 256 Hz)
sampling_rate = 256
n_channels = 4
window_size = sampling_rate * 1  # 1 second = 256 samples
buffer = np.zeros((window_size, n_channels))

# Reading new data into the buffer while deleting the oldest data
print("Streaming EEG and filling buffer...")
print("Calibrating baseline focus… please relax for 30 s.")
baseline_samples = collections.deque(maxlen=sampling_rate * 30)  # 30 s buffer

while len(baseline_samples) < baseline_samples.maxlen:
    sample, _ = inlet.pull_sample()
    if any(val < -800 for val in sample[:4]):
        continue
    buffer = np.roll(buffer, -1, axis=0)
    buffer[-1, :] = sample[:4]
    # --- same filtering & PSD code as before, but compute focus_raw only ---
    freqs, psd = welch(buffer, fs=sampling_rate, window="hann",
                       nperseg=256, noverlap=128, axis=0)
    theta = psd[(freqs>=4)&(freqs<8)].mean()
    alpha = psd[(freqs>=8)&(freqs<12)].mean()
    beta  = psd[(freqs>=13)&(freqs<30)].mean()
    focus_raw = beta / (theta + alpha + 1e-6)
    baseline_samples.append(focus_raw)

baseline = np.median(baseline_samples)
print(f"Baseline focus = {baseline:.3f}")


prev_focus = 0.5    # start near neutral
alpha = 0.2         # smoothing factor (0.1 = very smooth, 0.3 = quicker)
slow_focus = 0.5      # start neutral
alpha_slow = 0.05     # small = very smooth (≈ 20‑s time‑constant)
while True:
    sample, timestamp = inlet.pull_sample()
    # Check if the channel reads -1000 and skip if so
    if -1000 in sample[:4]:
        continue
    buffer = np.roll(buffer, -1, axis=0)       # Shift buffer left by 1
    buffer[-1, :] = sample[:4]                     # Insert new sample at the end

    # Optional: show first channel value to confirm updates
    # print(f"{timestamp:.3f} | CH1: {sample[0]:.4f}")

    # Apply filters: notch (60 Hz) + high-pass (1 Hz)
    notch_freq = 60.0
    q = 30.0  # Quality factor for notch
    b_notch, a_notch = iirnotch(notch_freq, q, fs=sampling_rate)
    b_hp, a_hp = butter(2, 1 / (sampling_rate / 2), btype='high')  # 1 Hz HPF

    filtered = filtfilt(b_notch, a_notch, buffer, axis=0)
    filtered = filtfilt(b_hp, a_hp, filtered, axis=0)

        # --- Compute Power Spectral Density (Welch) ---
    freqs, psd = welch(
        filtered,                # 1‑s window, shape (256, 4)
        fs=sampling_rate,
        window="hann",
        nperseg=256,
        noverlap=128,
        axis=0
    )

    # --- Extract band powers (mean across channels) ---
    theta_mask = (freqs >= 4) & (freqs < 8)
    alpha_mask = (freqs >= 8) & (freqs < 12)
    beta_mask  = (freqs >= 13) & (freqs < 30)

    theta = psd[theta_mask].mean(axis=0).mean()
    alpha = psd[alpha_mask].mean(axis=0).mean()
    beta  = psd[beta_mask].mean(axis=0).mean()

    # --- Compute raw focus index ---
    focus_raw = beta / (theta + alpha + 1e-6)
    focus_scaled = 1 / (1 + np.exp(-3 * (focus_raw / baseline - 1)))  # 0–1

    ma_window.append(focus_scaled)
    if len(ma_window) < ma_window.maxlen:
        continue  # wait until the window is full

    focus_scaled = sum(ma_window) / len(ma_window)

    slow_focus = alpha_slow * focus_scaled + (1 - alpha_slow) * slow_focus
    focus_scaled = slow_focus     # use the smoothed value from here on


    # --- Publish scaled focus directly ---
    msg = {
        "ts": time.time(),
        "focus": round(float(focus_scaled), 3)
    }
    pub.send_json(msg)

    print(f"Focus (scaled): {focus_scaled:.3f}")

    




