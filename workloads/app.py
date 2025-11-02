from flask import Flask, render_template, jsonify, request
import threading
import random
import time
from scheduler import Scheduler, Job

app = Flask(__name__)

# Create schedulers with speed factors
sched_cpu = Scheduler("CPU", speed_factor=1.0)
sched_gpu = Scheduler("GPU", speed_factor=0.6)
sched_sjf = Scheduler("GPU + SJF", speed_factor=0.4, use_sjf=True)

schedulers = [sched_cpu, sched_gpu, sched_sjf]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit_job", methods=["POST"])
def submit_job():
    runtime = random.randint(3, 10)  # simulate job runtime
    job_id = f"job_{random.randint(1000,9999)}"

    job = Job(job_id, runtime)

    for sched in schedulers:
        sched.submit(job)

    threads = []
    for sched in schedulers:
        t = threading.Thread(target=sched.run)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return jsonify({"message": "Jobs completed"})


@app.route("/usage_data")
def usage_data():
    data = []
    for sched in schedulers:
        data.append({
            "name": sched.name,
            "usage": sched.get_usage(),
            "total_time": sched.total_time,
            "running": sched.running
        })
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
