# scheduler.py
# Greedy priority-aware scheduler with runtime simulation using threads

from operator import attrgetter
from threading import Thread, Lock
import time

class Scheduler:
    def __init__(self, gpu_nodes):
        self.gpu_nodes = gpu_nodes
        self.queue = []
        self.jobs = {}          # job_id -> job
        self.lock = Lock()
        self._stop = False

    def submit_job(self, job):
        with self.lock:
            self.queue.append(job)
            self.jobs[job.job_id] = job
        return job.job_id

    def schedule_once(self):
        # Try to schedule queued jobs.
        with self.lock:
            # consider only QUEUED jobs
            queued = [j for j in self.queue if j.state == "QUEUED"]
            # sort by priority desc then by runtime desc (larger first helps packing)
            queued.sort(key=lambda j: (j.priority, j.runtime_seconds), reverse=True)
        for job in queued:
            placed = False
            # sort nodes by available_mem descending (pack on bigger free first)
            nodes = sorted(self.gpu_nodes, key=lambda n: n.available_mem, reverse=True)
            for node in nodes:
                if node.allocate(job):
                    placed = True
                    # start runtime simulation thread
                    t = Thread(target=self._run_job_thread, args=(job, node), daemon=True)
                    t.start()
                    print(f"[{time.strftime('%X')}] SCHEDULED {job.job_id} -> node {node.node_id} (mem {job.gpu_mem}, cores {job.gpu_cores}, rt {job.runtime_seconds}s)")
                    break
            if placed:
                # remove from queue list (it remains in jobs dict)
                with self.lock:
                    if job in self.queue:
                        self.queue.remove(job)
            else:
                # cannot place now
                pass

    def _run_job_thread(self, job, node):
        try:
            job.start_time = time.time()
            # simulate progress by sleeping in small increments (to let UI show intermediate util)
            remaining = job.runtime_seconds
            step = 1
            while remaining > 0:
                time.sleep(min(step, remaining))
                remaining -= step
                # append node util snapshot so history updates during run
                node._append_history()
                if job.state == "CANCELLED":
                    # early exit
                    break
            # finished normally -> release
            node.release(job)
            print(f"[{time.strftime('%X')}] COMPLETED {job.job_id} on node {node.node_id}")
        except Exception as e:
            job.state = "FAILED"
            print(f"Job {job.job_id} failed: {e}")

    def cancel_job(self, job_id):
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return False
            # if queued remove
            if job in self.queue:
                self.queue.remove(job)
                job.state = "CANCELLED"
                return True
            # if running mark cancelled (the runtime thread checks this)
            job.state = "CANCELLED"
            return True

    def all_jobs(self):
        with self.lock:
            return list(self.jobs.values())

    def queue_length(self):
        with self.lock:
            return len(self.queue)
