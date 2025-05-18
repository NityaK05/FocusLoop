# eye/calibration.py

import time
import zmq
from bcea import compute_bcea

def collect_baseline(zmq_addr="tcp://localhost:5556", duration=30):
    print(f"\n[*] Starting baseline collection for {duration}s…\n", flush=True)
    ctx = zmq.Context()
    sub = ctx.socket(zmq.SUB)
    sub.connect(zmq_addr)
    sub.setsockopt_string(zmq.SUBSCRIBE, "")

    xs, ys = [], []
    start = time.time()
    next_status = start + 5
    while True:
        now = time.time()
        # break when duration elapsed
        if now - start >= duration:
            break

        try:
            data = sub.recv_json(flags=zmq.NOBLOCK)
            if data.get("valid"):
                xs.append(data["x"])
                ys.append(data["y"])
        except zmq.Again:
            # no message waiting
            pass

        # status update every 5s
        if now >= next_status:
            elapsed = int(now - start)
            print(f"  …{elapsed}s elapsed, collected {len(xs)} valid samples", flush=True)
            next_status += 5

        time.sleep(0.005)  # small sleep to avoid 100% CPU

    baseline = compute_bcea(xs, ys)
    with open("baseline_bcea.txt", "w") as f:
        f.write(str(baseline))
    print(f"\n[✓] Saved baseline BCEA = {baseline:.4f} deg²\n", flush=True)

if __name__ == "__main__":
    collect_baseline()
