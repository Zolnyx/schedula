import random

def random_job_id():
    return f"job_{random.randint(1000, 9999)}"

def random_job_params():
    return {
        "gpu_req": random.randint(1, 2),
        "mem_req": random.randint(2, 8),
        "runtime": random.randint(3, 10),
    }
