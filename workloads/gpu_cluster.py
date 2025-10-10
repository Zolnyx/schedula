# gpu_cluster.py
# GPU node simulation

from threading import Lock

class GPUNode:
    def __init__(self, node_id, total_mem=16000, total_cores=8):
        self.node_id = str(node_id)
        self.total_mem = total_mem
        self.total_cores = total_cores
        self.available_mem = total_mem
        self.available_cores = total_cores
        self.running_jobs = []
        self.lock = Lock()
        # history for visualization (list of recent utilization points)
        self.util_history = []  # list of (timestamp, used_mem, used_cores)

    def can_allocate(self, job):
        return job.gpu_mem <= self.available_mem and job.gpu_cores <= self.available_cores

    def allocate(self, job):
        with self.lock:
            if self.can_allocate(job):
                self.available_mem -= job.gpu_mem
                self.available_cores -= job.gpu_cores
                self.running_jobs.append(job)
                job.assigned_node = self.node_id
                job.assigned_time = __import__("time").time()
                job.start_time = job.assigned_time
                job.state = "RUNNING"
                # record current util snapshot
                self._append_history()
                return True
            return False

    def release(self, job):
        with self.lock:
            if job in self.running_jobs:
                self.running_jobs.remove(job)
                self.available_mem += job.gpu_mem
                self.available_cores += job.gpu_cores
                job.end_time = __import__("time").time()
                job.state = "COMPLETED"
                # record current util snapshot
                self._append_history()
                return True
            return False

    def current_used_mem(self):
        return self.total_mem - self.available_mem

    def current_used_cores(self):
        return self.total_cores - self.available_cores

    def to_dict(self):
        return {
            "node_id": self.node_id,
            "total_mem": self.total_mem,
            "total_cores": self.total_cores,
            "available_mem": self.available_mem,
            "available_cores": self.available_cores,
            "running_jobs": [j.to_dict() for j in self.running_jobs],
            "util_history": list(self.util_history),
        }

    def _append_history(self):
        import time
        ts = time.time()
        used_mem = self.current_used_mem()
        used_cores = self.current_used_cores()
        self.util_history.append((ts, used_mem, used_cores))
        # keep history length limited
        if len(self.util_history) > 200:
            self.util_history.pop(0)

    def __repr__(self):
        return f"GPUNode({self.node_id}, free_mem={self.available_mem}, free_cores={self.available_cores})"
