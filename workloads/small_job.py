# job.py
# Job representation

import time
import uuid

class Job:
    def __init__(self, gpu_mem, gpu_cores, runtime_seconds, priority=1, user="user"):
        self.job_id = str(uuid.uuid4())[:8]
        self.gpu_mem = gpu_mem
        self.gpu_cores = gpu_cores
        self.runtime_seconds = runtime_seconds
        self.priority = priority
        self.user = user
        self.assigned_node = None
        self.assigned_time = None
        self.start_time = None
        self.end_time = None
        self.state = "QUEUED"   # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED

    def to_dict(self):
        return {
            "job_id": self.job_id,
            "gpu_mem": self.gpu_mem,
            "gpu_cores": self.gpu_cores,
            "runtime_seconds": self.runtime_seconds,
            "priority": self.priority,
            "user": self.user,
            "assigned_node": self.assigned_node,
            "state": self.state,
            "assigned_time": self.assigned_time,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }

    def __repr__(self):
        return f"Job({self.job_id}, mem={self.gpu_mem}, cores={self.gpu_cores}, rt={self.runtime_seconds}, prio={self.priority}, state={self.state})"
