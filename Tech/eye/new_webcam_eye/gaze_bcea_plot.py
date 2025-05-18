# gaze_bcea_plot.py

import zmq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

# --- ZeroMQ subscriber (gets gaze JSON) ---
ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://127.0.0.1:5557")
sub.setsockopt_string(zmq.SUBSCRIBE, "")   # receive all messages

# --- Data buffers ---
times = []
bcea_vals = []
start_time = time.time()

# --- Figure setup ---
fig, ax = plt.subplots(figsize=(8, 4))
line, = ax.plot([], [], lw=2)
ax.set_xlim(0, 30)        # 30-second rolling window
ax.set_ylim(0, 1e5)       # adjust if your BCEA range is different
ax.set_xlabel("Time (s)")
ax.set_ylabel("BCEA (px²)")
ax.set_title("Live 95% BCEA")

# --- Animation update ---
def update(frame):
    # drain any queued messages
    while sub.poll(timeout=0):
        msg = sub.recv_json()
        t_now = msg["ts"] - start_time
        bcea  = msg.get("bcea")
        if bcea is not None:
            times.append(t_now)
            bcea_vals.append(bcea)

    # keep last 30 s of data
    while times and (times[-1] - times[0] > 30):
        times.pop(0)
        bcea_vals.pop(0)

    if times:
        line.set_data(times, bcea_vals)
        ax.set_xlim(max(0, times[-1] - 30), times[-1])
        # optionally auto-scale y:
        # ax.set_ylim(min(bcea_vals), max(bcea_vals))
    return line,

# --- Start animation ---
ani = animation.FuncAnimation(fig, update, interval=200, blit=True)
plt.show()
