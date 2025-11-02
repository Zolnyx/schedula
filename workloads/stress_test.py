import requests
import time
import random

URL = "http://127.0.0.1:5000/submit"

for i in range(20):
    data = {
        "gpu": random.randint(1, 2),
        "mem": random.randint(2, 8),
        "runtime": random.randint(3, 10),
    }
    res = requests.post(URL, data=data)
    print(res.json())
    time.sleep(0.5)
