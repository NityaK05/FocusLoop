# dispersion.py
import time
import json
from collections import deque
import zmq
from bcea import compute_bcea, normalize_bcea

baseline = float(open("baseline_bcea.txt").read())

ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://localhost:5556")  # from gaze_ws_server.py
sub.setsockopt_string(zmq.SUBSCRIBE, "")
pub = ctx.socket(zmq.PUB)
pub.bind("tcp://*:5557")             # dispersion out on 5557

window = deque(maxlen=15)  # ~500ms at 30Hz

def publish():
    valid = [pt for pt in window if pt is not None]
    if len(valid) < window.maxlen * 0.6:
        disp = None
    else:
        xs, ys = zip(*valid)
        raw = compute_bcea(xs, ys)
        disp = normalize_bcea(raw, baseline)
    msg = {"ts": time.time(), "dispersion": disp}
    pub.send_string("/dispersion_score " + json.dumps(msg))

if __name__ == "__main__":
    next_time = time.time()
    while True:
        try:
            _, raw = sub.recv_multipart(flags=zmq.NOBLOCK)
            data = json.loads(raw)
            window.append((data["x"], data["y"]) if data["valid"] else None)
        except zmq.Again:
            pass

        if time.time() >= next_time:
            publish()
            next_time += 0.025
        time.sleep(0.001)
