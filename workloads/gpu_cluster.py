# gpu_cluster.py
class GPUNode:
    def __init__(self, node_id, total_mem=16000, total_cores=8):
        self.node_id = node_id
        self.total_mem = total_mem
        self.total_cores = total_cores
        self.available_mem = total_mem
        self.available_cores = total_cores
        self.running_jobs = []

    def can_allocate(self, job):
        return job.gpu_mem <= self.available_mem and job.gpu_cores <= self.available_cores

    def allocate(self, job):
        if self.can_allocate(job):
            self.available_mem -= job.gpu_mem
            self.available_cores -= job.gpu_cores
            self.running_jobs.append(job)
            job.assigned_gpu = self.node_id
            return True
        return False

    def release(self, job):
        if job in self.running_jobs:
            self.running_jobs.remove(job)
            self.available_mem += job.gpu_mem
            self.available_cores += job.gpu_cores

    def __repr__(self):
        return f"GPUNode({self.node_id}, free_mem={self.available_mem}, free_cores={self.available_cores})"
