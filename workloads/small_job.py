# job.py
class Job:
    def __init__(self, job_id, gpu_mem, gpu_cores, runtime, priority=1):
        self.job_id = job_id
        self.gpu_mem = gpu_mem
        self.gpu_cores = gpu_cores
        self.runtime = runtime
        self.priority = priority
        self.assigned_gpu = None

    def __repr__(self):
        return f"Job({self.job_id}, mem={self.gpu_mem}, cores={self.gpu_cores}, prio={self.priority})"
