# main.py
from gpu_cluster import GPUNode
from scheduler import Scheduler
from utils import generate_random_jobs
import time

def main():
    # Create 2 GPU nodes
    gpus = [GPUNode(node_id=1, total_mem=16000, total_cores=8),
            GPUNode(node_id=2, total_mem=12000, total_cores=6)]

    # Generate random jobs
    jobs = generate_random_jobs(6)
    print("\n🎯 Generated Jobs:")
    for job in jobs:
        print(job)

    scheduler = Scheduler(gpus)
    unassigned = scheduler.schedule(jobs)

    print("\n📊 GPU Node Status:")
    for g in gpus:
        print(g, "| Running:", g.running_jobs)

    print("\n🚫 Unassigned Jobs:", unassigned)

    # Optional: simulate job completion
    print("\n⌛ Simulating job completion...")
    time.sleep(2)
    gpus[0].release(gpus[0].running_jobs[0])
    print("Job completed! Updated node status:")
    for g in gpus:
        print(g)

if __name__ == "__main__":
    main()
