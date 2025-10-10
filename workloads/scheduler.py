# scheduler.py
from operator import attrgetter

class Scheduler:
    def __init__(self, gpu_nodes):
        self.gpu_nodes = gpu_nodes

    def schedule(self, jobs):
        # Sort jobs by priority (high to low)
        jobs.sort(key=attrgetter("priority"), reverse=True)
        unassigned = []

        for job in jobs:
            allocated = False
            # Try to allocate on the node with most free memory
            sorted_nodes = sorted(self.gpu_nodes, key=lambda g: g.available_mem, reverse=True)
            for node in sorted_nodes:
                if node.allocate(job):
                    print(f"✅ Job {job.job_id} assigned to GPU-{node.node_id}")
                    allocated = True
                    break
            if not allocated:
                print(f"❌ Job {job.job_id} could not be scheduled.")
                unassigned.append(job)

        return unassigned
