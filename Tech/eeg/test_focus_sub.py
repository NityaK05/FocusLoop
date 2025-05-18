import zmq, pprint

ctx = zmq.Context()
sub = ctx.socket(zmq.SUB)
sub.connect("tcp://127.0.0.1:5556")
sub.setsockopt_string(zmq.SUBSCRIBE, "")   # receive all messages

print("Listening for focus JSON…  (Ctrl+C to stop)")
while True:
    msg = sub.recv_json()
    pprint.pprint(msg)
