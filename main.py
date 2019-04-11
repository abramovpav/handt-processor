import re
from datetime import datetime
from functools import reduce

import serial
import time

from elasticsearch import Elasticsearch

es = Elasticsearch()
port = "/dev/ttyUSB0"
ard = serial.Serial(port, 9600, timeout=5)

running = True

pattern = re.compile(r"H(?P<humidity>[0-9\.]+)\sC(?P<temperature>[0-9\.]+)")

storage = []

while running:
    msg = ard.read(ard.inWaiting())  # read everything in the input buffer
    if len(msg):

        data = pattern.findall(str(msg))
        storage += data

        if len(storage) >= 5:
            h_t_sum = reduce(
                lambda x, y: (
                    float(x[0]) + float(y[0]),
                    float(x[1]) + float(y[1]),
                ),
                storage,
            )
            doc = {
                "date": datetime.utcnow(),
                "humidity": h_t_sum[0] / len(storage),
                "temperature": h_t_sum[1] / len(storage),
            }
            print("doc", doc)
            res = es.index(index="test-index", doc_type="test", body=doc)
            storage = []

        print(msg, data)
    time.sleep(2*5)
