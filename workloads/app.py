from flask import Flask, render_template, jsonify, request
import threading
import random
import time
import numpy as np 
# Import our "manual" Numba functions
from scheduler import Scheduler, Job, single_core_mult, parallel_mult

app = Flask(__name__)

# --- Schedulers are defined as before ---
sched_cpu = Scheduler("Single-Core (Numba)", target='single')
sched_parallel = Scheduler("Parallel-Core (Numba)", target='parallel')
sched_sjf = Scheduler("Parallel-Core + SJF", use_sjf=True, target='parallel')

schedulers = [sched_cpu, sched_parallel, sched_sjf]
# We only need one master thread
simulation_thread = None


# -----------------------------------------------------------------
# --- WARM-UP FUNCTION ---
# This pre-compiles both functions for both job sizes.
# -----------------------------------------------------------------
def warmup_numba():
    print("--- Warming up Numba JIT compiler... (This will take a minute) ---")
    
    # --- Job Size 1: 512x512 ---
    print("Compiling for 512x512...")
    A_512 = np.random.rand(512, 512).astype(np.float64) 
    B_512 = np.random.rand(512, 512).astype(np.float64)
    C_512 = np.zeros((512, 512), dtype=np.float64)
    
    single_core_mult(A_512, B_512, C_512)
    parallel_mult(A_512, B_512, C_512)

    # --- Job Size 2: 1024x1024 ---
    print("Compiling for 1024x1024...")
    A_1024 = np.random.rand(1024, 1024).astype(np.float64) 
    B_1024 = np.random.rand(1024, 1024).astype(np.float64)
    C_1024 = np.zeros((1024, 1024), dtype=np.float64)
    
    single_core_mult(A_1024, B_1024, C_1024)
    parallel_mult(A_1024, B_1024, C_1024)
    
    print("--- Numba is ready. Starting web server. ---")
# -----------------------------------------------------------------


# --- === THE FIX === ---
# This is the "Conductor" function that runs our tests
# one after another, inside its own thread.
def run_sequential_simulation(job_batch):
    """
    Runs each scheduler one by one to prevent
    thread contention.
    """
    
    # Run Test 1: Single-Core
    sched_cpu.jobs = list(job_batch)
    sched_cpu.run()
    
    # Run Test 2: Parallel
    sched_parallel.jobs = list(job_batch)
    sched_parallel.run()
    
    # Run Test 3: Parallel + SJF
    sched_sjf.jobs = list(job_batch)
    sched_sjf.run()
# --- === END FIX === ---


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run_simulation", methods=["POST"])
def run_simulation():
    global simulation_thread
    
    # Stop any previous simulation
    for sched in schedulers:
        sched.reset() 
        
    if simulation_thread and simulation_thread.is_alive():
        # This is a simple way to stop the old thread,
        # our sched.running = False logic in scheduler.py will handle it
        pass

    # --- 20 lighter jobs ---
    job_batch = []
    job_sizes = ([512] * 10) + ([1024] * 10)
    random.shuffle(job_sizes) 
    
    for i, size in enumerate(job_sizes):
        job_batch.append(Job(job_id=f"job_{i}", matrix_size=size))

    # --- === THE FIX (Part 2) === ---
    # We launch the *Conductor* in a thread,
    # and the main Flask thread is now free.
    simulation_thread = threading.Thread(
        target=run_sequential_simulation, 
        args=(job_batch,)
    )
    simulation_thread.start()
    # --- === END FIX === ---

    return jsonify({"message": f"{len(job_sizes)} jobs submitted."})


@app.route("/usage_data")
def usage_data():
    """Endpoint for the frontend to poll for data."""
    data = []
    for sched in schedulers:
        data.append({
            "name": sched.name,
            "job_times": sched.get_job_times(), 
            "total_time": sched.total_time,
            "running": sched.running
        })
    return jsonify(data)


if __name__ == "__main__":
    warmup_numba() # Run the thorough warm-up
    
    # Enable threading so Flask can handle
    # /usage_data polls while the Conductor thread is running.
    app.run(debug=True, use_reloader=False, threaded=True)