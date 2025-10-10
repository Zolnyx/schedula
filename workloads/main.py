# app.py
# Main application that runs scheduler and serves a Flask UI with Chart.js visualization

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from small_job import Job
from gpu_cluster import GPUNode
from scheduler import Scheduler
from threading import Thread
import time

# create nodes
nodes = [
    GPUNode(node_id="gpu-1", total_mem=16000, total_cores=8),
    GPUNode(node_id="gpu-2", total_mem=12000, total_cores=6),
]

# create scheduler
sched = Scheduler(nodes)

# background scheduler loop thread
def scheduler_loop():
    while True:
        try:
            sched.schedule_once()
        except Exception as e:
            print("Scheduler loop error:", e)
        time.sleep(1)

t = Thread(target=scheduler_loop, daemon=True)
t.start()

app = Flask(__name__)
CORS(app)

# API endpoints

@app.route("/api/submit", methods=["POST"])
def api_submit():
    data = request.json or {}
    gpu_mem = int(data.get("gpu_mem", 2000))
    gpu_cores = int(data.get("gpu_cores", 1))
    runtime_seconds = int(data.get("runtime_seconds", 10))
    priority = int(data.get("priority", 1))
    user = data.get("user", "user")
    job = Job(gpu_mem=gpu_mem, gpu_cores=gpu_cores, runtime_seconds=runtime_seconds, priority=priority, user=user)
    job_id = sched.submit_job(job)
    return jsonify({"job_id": job_id})

@app.route("/api/status")
def api_status():
    nodes_state = {n.node_id: n.to_dict() for n in nodes}
    jobs = [j.to_dict() for j in sched.all_jobs()]
    return jsonify({"nodes": nodes_state, "jobs": jobs, "queue_len": sched.queue_length()})

@app.route("/api/cancel/<job_id>", methods=["POST"])
def api_cancel(job_id):
    ok = sched.cancel_job(job_id)
    return jsonify({"ok": ok})

# UI page (single-file HTML with Chart.js via CDN)
INDEX_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Schedula — Local GPU Scheduler</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
      body { font-family: Arial, sans-serif; margin: 16px; }
      .grid { display: grid; grid-template-columns: 1fr 420px; gap: 16px; }
      .card { padding: 12px; border: 1px solid #ddd; border-radius: 6px; background: #fff; }
      .job { padding: 6px; border-bottom: 1px solid #eee; }
      .job:last-child { border-bottom: none; }
      label { display:block; margin-top:8px; }
      input, select { width: 100%; padding:6px; box-sizing: border-box; }
      button { margin-top:8px; padding:8px 12px; }
      .node-title { font-weight: bold; margin-bottom:8px; }
    </style>
  </head>
  <body>
    <h2>Schedula — Local GPU Scheduler (Simulation)</h2>
    <div class="grid">
      <div class="card">
        <div style="display:flex; gap:12px;">
          <div style="flex:1">
            <h3>Submit Job</h3>
            <label>GPU Memory (MB)</label>
            <input id="gpu_mem" value="2000">
            <label>GPU Cores</label>
            <input id="gpu_cores" value="1">
            <label>Runtime (seconds)</label>
            <input id="runtime" value="10">
            <label>Priority (higher = scheduled first)</label>
            <input id="priority" value="1">
            <label>User</label>
            <input id="user" value="vaibhav">
            <button onclick="submitJob()">Submit Job</button>
            <div id="submit_result" style="margin-top:8px"></div>
          </div>
          <div style="width:320px;">
            <h3>Cluster Status</h3>
            <div id="nodes_container"></div>
          </div>
        </div>

        <h3>Jobs</h3>
        <div id="jobs_container"></div>
      </div>

      <div class="card">
        <h3>GPU Memory Utilization (recent)</h3>
        <canvas id="memChart" width="400" height="300"></canvas>
        <h3 style="margin-top:16px">GPU Cores Utilization (recent)</h3>
        <canvas id="coreChart" width="400" height="300"></canvas>
      </div>
    </div>

    <script>
      const memCtx = document.getElementById('memChart').getContext('2d');
      const coreCtx = document.getElementById('coreChart').getContext('2d');
      let memChart = null;
      let coreChart = null;

      async function fetchStatus(){
        let resp = await fetch('/api/status');
        let data = await resp.json();
        return data;
      }

      function renderNodes(nodes){
        const container = document.getElementById('nodes_container');
        container.innerHTML = '';
        for (const nid in nodes){
          const n = nodes[nid];
          const div = document.createElement('div');
          div.innerHTML = `<div class="node-title">${nid}</div>
            <div>Free mem: ${n.available_mem} MB / ${n.total_mem} MB</div>
            <div>Free cores: ${n.available_cores} / ${n.total_cores}</div>
            <div>Running jobs: ${n.running_jobs.length}</div>`;
          container.appendChild(div);
        }
      }

      function renderJobs(jobs){
        const cont = document.getElementById('jobs_container');
        cont.innerHTML = '';
        jobs.sort((a,b)=> (b.priority - a.priority));
        for (const j of jobs){
          const div = document.createElement('div');
          div.className = 'job';
          div.innerHTML = `<div><b>${j.job_id}</b> — ${j.state} — user:${j.user} — prio:${j.priority}</div>
            <div>mem:${j.gpu_mem} cores:${j.gpu_cores} rt:${j.runtime_seconds}s assigned:${j.assigned_node || '-'}</div>
            <div style="margin-top:6px;"><button onclick="cancelJob('${j.job_id}')">Cancel</button></div>`;
          cont.appendChild(div);
        }
      }

      function createCharts(nodes){
        const labels = []; // shared labels (time)
        const datasetsMem = [];
        const datasetsCore = [];
        let i=0;
        for (const nid in nodes){
          const n = nodes[nid];
          // build data from util_history: use last 30 points
          const history = n.util_history.slice(-40);
          const times = history.map(h=> new Date(h[0]*1000).toLocaleTimeString());
          if (labels.length < times.length){
            labels.splice(0, labels.length, ...times);
          }
          const dataMem = history.map(h=> h[1]);
          const dataCore = history.map(h=> h[2]);
          datasetsMem.push({
            label: nid,
            data: dataMem,
            fill: false,
            borderWidth: 2,
            tension: 0.2,
          });
          datasetsCore.push({
            label: nid,
            data: dataCore,
            fill: false,
            borderWidth: 2,
            tension: 0.2,
          });
          i++;
        }
        // create or update memChart
        if (memChart){
          memChart.data.labels = labels;
          memChart.data.datasets = datasetsMem;
          memChart.update();
        } else {
          memChart = new Chart(memCtx, {
            type: 'line',
            data: { labels: labels, datasets: datasetsMem },
            options: {
              responsive: true,
              scales: {
                y: { title: { display: true, text: 'Used memory (MB)' } }
              }
            }
          });
        }
        if (coreChart){
          coreChart.data.labels = labels;
          coreChart.data.datasets = datasetsCore;
          coreChart.update();
        } else {
          coreChart = new Chart(coreCtx, {
            type: 'line',
            data: { labels: labels, datasets: datasetsCore },
            options: {
              responsive: true,
              scales: {
                y: { title: { display: true, text: 'Used cores' }, beginAtZero:true }
              }
            }
          });
        }
      }

      async function refresh(){
        try {
          const data = await fetchStatus();
          renderNodes(data.nodes);
          renderJobs(data.jobs);
          createCharts(data.nodes);
          document.getElementById('submit_result').innerText = `Queue length: ${data.queue_len}`;
        } catch (e){
          console.error(e);
        }
      }

      async function submitJob(){
        const gpu_mem = document.getElementById('gpu_mem').value;
        const gpu_cores = document.getElementById('gpu_cores').value;
        const runtime = document.getElementById('runtime').value;
        const priority = document.getElementById('priority').value;
        const user = document.getElementById('user').value;
        const payload = {
          gpu_mem: parseInt(gpu_mem),
          gpu_cores: parseInt(gpu_cores),
          runtime_seconds: parseInt(runtime),
          priority: parseInt(priority),
          user: user
        };
        const resp = await fetch('/api/submit', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const j = await resp.json();
        document.getElementById('submit_result').innerText = `Submitted job ${j.job_id}`;
      }

      async function cancelJob(job_id){
        await fetch('/api/cancel/' + job_id, { method: 'POST' });
        await refresh();
      }

      // poll every 1.5s
      setInterval(refresh, 1500);
      refresh();
    </script>
  </body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

if __name__ == "__main__":
    print("Starting Schedula UI on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
