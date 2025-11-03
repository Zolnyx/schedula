import time
import random
import threading
import numpy as np
from numba import jit, prange # We are using jit and prange

# --- "Heavy Lifting" Function 1: Single-Core ---
@jit(nopython=True) # The classic, single-threaded JIT
def single_core_mult(A, B, C):
    """
    Performs matrix multiplication C = A * B on a SINGLE core.
    We write the loops manually to prevent auto-parallelization.
    """
    m, n = A.shape
    n, p = B.shape
    for i in range(m):
        for j in range(p):
            tmp = 0.
            for k in range(n):
                tmp += A[i, k] * B[k, j]
            C[i, j] = tmp

# --- "Heavy Lifting" Function 2: Parallel-Core ---
@jit(nopython=True, parallel=True) # The parallel-enabled JIT
def parallel_mult(A, B, C):
    """
    Performs matrix multiplication C = A * B on ALL cores.
    We use 'prange' to explicitly parallelize the outer loop.
    """
    m, n = A.shape
    n, p = B.shape
    
    # prange = "parallel range"
    for i in prange(m): 
        for j in range(p):
            tmp = 0.
            for k in range(n):
                tmp += A[i, k] * B[k, j]
            C[i, j] = tmp
# -------------------------------------------------

class Job:
    def __init__(self, job_id, matrix_size):
        self.job_id = job_id
        self.size = matrix_size
        
        # Create the actual data for the job
        self.A = np.random.rand(self.size, self.size).astype(np.float64)
        self.B = np.random.rand(self.size, self.size).astype(np.float64)
        self.C = np.zeros((self.size, self.size), dtype=np.float64)


class Scheduler:
    def __init__(self, name, use_sjf=False, target='single'):
        self.name = name
        self.use_sjf = use_sjf
        self.target = target # 'single' or 'parallel'
        self.jobs = []
        self.job_times = [] 
        self.total_time = 0
        self.running = False

    def submit(self, job):
        self.jobs.append(job)

    def reset(self):
        self.jobs = []
        self.job_times = []
        self.total_time = 0
        self.running = False

    def run(self):
        if not self.jobs:
            return

        self.job_times = []
        self.total_time = 0
        self.running = True

        if self.use_sjf:
            self.jobs.sort(key=lambda j: j.size)

        run_function = single_core_mult if self.target == 'single' else parallel_mult

        overall_start_time = time.perf_counter()

        for job in self.jobs:
            if not self.running:
                break
                
            job_start_time = time.perf_counter()
            run_function(job.A, job.B, job.C)
            job_end_time = time.perf_counter()
            
            job_duration = round(job_end_time - job_start_time, 4)
            self.job_times.append(job_duration)
            
            # --- === THE FIX === ---
            # Yield control back to the OS, so the Flask server
            # thread can respond to /usage_data requests.
            time.sleep(0.01)
            # --- === END FIX === ---

        self.total_time = round(time.perf_counter() - overall_start_time, 2)
        self.running = False
        print(f"{self.name} finished in {self.total_time} seconds")

    def get_job_times(self):
        return self.job_times