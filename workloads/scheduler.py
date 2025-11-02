import time
import random
import threading


class Job:
    def __init__(self, job_id, runtime):
        self.job_id = job_id
        self.runtime = runtime


class Scheduler:
    def __init__(self, name, speed_factor=1.0, use_sjf=False):
        self.name = name
        self.speed_factor = speed_factor
        self.use_sjf = use_sjf
        self.jobs = []
        self.usage_history = []
        self.total_time = 0
        self.running = False

    def submit(self, job):
        self.jobs.append(job)

    def run(self):
        if not self.jobs:
            return

        if self.use_sjf:
            # Sort by runtime (shortest job first)
            self.jobs.sort(key=lambda j: j.runtime)

        start_time = time.time()
        self.running = True

        for job in self.jobs:
            usage = random.randint(40, 100)
            self.usage_history.append(usage)

            # Simulate processing time (scaled by speed)
            simulated_runtime = job.runtime * self.speed_factor
            time.sleep(simulated_runtime * 0.2)

        self.total_time = round(time.time() - start_time, 2)
        self.running = False
        print(f"{self.name} finished in {self.total_time} seconds")

    def get_usage(self):
        return self.usage_history
