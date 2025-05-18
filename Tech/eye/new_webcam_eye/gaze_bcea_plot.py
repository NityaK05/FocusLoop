#!/usr/bin/env python3
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
raw_bcea_vals = []
start_time = time.time()

# --- Figure setup ---
fig, ax = plt.subplots(figsize=(8, 4))
line, = ax.plot([], [], lw=2)
ax.set_xlim(0, 30)        # 30-second rolling window
ax.set_ylim(0, 1)         # normalized BCEA in [0,1]
ax.set_xlabel("Time (s)")
ax.set_ylabel("Normalized BCEA")
ax.set_title("Live 95% BCEA (Normalized)")

# --- Animation update ---
def update(frame):
    # drain any queued messages
    while sub.poll(timeout=0):
        msg = sub.recv_json()
        t_now = msg["ts"] - start_time
        bcea  = msg.get("bcea")
        if bcea is not None:
            times.append(t_now)
            raw_bcea_vals.append(bcea)

    # keep last 30 s of data
    while times and (times[-1] - times[0] > 30):
        times.pop(0)
        raw_bcea_vals.pop(0)

    if times:
        # compute normalized values
        max_raw = max(raw_bcea_vals) or 1.0
        norm_vals = [v / max_raw for v in raw_bcea_vals]

        line.set_data(times, norm_vals)
        ax.set_xlim(max(0, times[-1] - 30), times[-1])
    return line,

# --- Start animation ---
ani = animation.FuncAnimation(fig, update, interval=200, blit=True)
plt.show()
