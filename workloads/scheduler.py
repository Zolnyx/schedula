from small_job import Job
from gpu_cluster import GPUCluster

class Scheduler:
    def __init__(self):
        self.cluster = GPUCluster()
        self.job_queue = []
        self.running_jobs = []
        self.completed_jobs = []

    def submit_job(self, job: Job):
        print(f"Submitting job {job.job_id}")
        self.job_queue.append(job)
        self.schedule()

    def schedule(self):
        for job in list(self.job_queue):  # iterate over a copy
            if self.cluster.allocate_resources(job.gpu_req, job.mem_req):
                self.job_queue.remove(job)
                self.running_jobs.append(job)
                job.run(self.cluster, self.on_job_complete)

    def on_job_complete(self, job: Job):
        self.running_jobs.remove(job)
        self.completed_jobs.append(job)
        print(f"Job {job.job_id} completed.")
        self.schedule()  # try to run next queued job

    def get_status(self):
        return {
            "queued": len(self.job_queue),
            "running": len(self.running_jobs),
            "completed": len(self.completed_jobs),
            "available_gpus": self.cluster.available_gpus,
            "available_mem": self.cluster.available_mem,
            "total_gpus": self.cluster.total_gpus,
            "total_mem": self.cluster.total_mem,
        }

scheduler = Scheduler()
