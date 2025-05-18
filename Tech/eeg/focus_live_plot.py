import zmq
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

# --- ZeroMQ subscriber (gets focus JSON) ---
ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://127.0.0.1:5556")
sub.setsockopt_string(zmq.SUBSCRIBE, "")   # receive all messages

# --- Data buffers ---
times = []
focus_vals = []
start_time = time.time()

plt.style.use("seaborn-v0_8")  
fig, ax = plt.subplots(figsize=(8, 4))
line, = ax.plot([], [], lw=2)
ax.set_xlim(0, 30)        
ax.set_ylim(0, 1)
ax.set_xlabel("Time (s)")
ax.set_ylabel("Focus (0‑1)")
ax.set_title("Live Focus Index")


def update(frame):
    while sub.poll(timeout=0):      
        msg = sub.recv_json()
        t_now = msg["ts"] - start_time
        focus = msg["focus"]

        times.append(t_now)
        focus_vals.append(focus)

    # keep last 30 s of points
    while times and times[-1] - times[0] > 30:
        times.pop(0)
        focus_vals.pop(0)

    if times:
        line.set_data(times, focus_vals)
        ax.set_xlim(max(0, times[-1] - 30), times[-1])

    return line,

# --- Start animation ---
ani = animation.FuncAnimation(fig, update, interval=200, blit=True)
plt.show()

