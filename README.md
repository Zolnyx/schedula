# Schedula: Resource-Aware Scheduling for Efficient GPU Utilization in Cloud Platforms

The goal is to create a framework similar to solutions like parvagpu, but for a smaller scale.

pip install -r requirements.txt
Run - app main.py

Schedula: Resource-Aware GPU Scheduling Simulator

Schedula is a lightweight simulation framework for exploring GPU resource scheduling strategies in cloud-like environments.
It allows you to visualize and compare three different scheduling scenarios:

Jobs without GPU awareness – all jobs run on CPU-like resources (no optimization).

Jobs with basic GPU scheduling – jobs use GPU and memory constraints, first-come-first-serve.

Jobs with intelligent scheduling (e.g. SJF) – shortest-job-first scheduling to optimize GPU utilization.

🚀 Features

Real-time web dashboard (Flask + Chart.js)

GPU & Memory usage graphs for each scheduling mode

Multi-threaded job simulation

Automatic stress-test job submission

Easily extensible for new scheduling algorithms (e.g., Round Robin, Priority Queue, etc.)