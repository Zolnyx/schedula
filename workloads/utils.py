# utils.py
import random
from small_job import Job

def generate_random_jobs(n=5):
    jobs = []
    for i in range(n):
        gpu_mem = random.choice([2000, 4000, 6000, 8000])
        gpu_cores = random.choice([1, 2, 4])
        runtime = random.choice([2, 5, 8])
        priority = random.choice([1, 2, 3])
        jobs.append(Job(f"Job-{i+1}", gpu_mem, gpu_cores, runtime, priority))
    return jobs
 