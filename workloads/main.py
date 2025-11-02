from flask import Flask, render_template_string, jsonify, request
from scheduler import scheduler
from small_job import Job
from utils import random_job_id
import random

app = Flask(__name__)

# Simple in-memory HTML template (no separate folder needed)
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Schedula Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body style="font-family: Arial; text-align:center;">
  <h2>📊 Schedula: GPU Scheduler Dashboard</h2>
  <canvas id="chart" width="400" height="200"></canvas>
  <form id="form">
    <input name="gpu" type="number" min="1" max="4" placeholder="GPU Req" required>
    <input name="mem" type="number" min="1" max="32" placeholder="Mem Req" required>
    <button type="submit">Submit Job</button>
  </form>
  <h3 id="status"></h3>
  <script>
    const ctx = document.getElementById('chart');
    const chart = new Chart(ctx, {
      type: 'bar',
      data: { labels: ['Avail GPUs','Avail Mem','Queued','Running','Completed'],
              datasets: [{ label:'Scheduler', data:[0,0,0,0,0] }] },
      options: { scales: { y: { beginAtZero: true } } }
    });
    async function refresh() {
      const res = await fetch('/status');
      const s = await res.json();
      chart.data.datasets[0].data = [s.available_gpus,s.available_mem,s.queued,s.running,s.completed];
      chart.update();
      document.getElementById('status').innerText =
        `Queued: ${s.queued} | Running: ${s.running} | Completed: ${s.completed}`;
    }
    setInterval(refresh, 1000);
    document.getElementById('form').addEventListener('submit', async e=>{
      e.preventDefault();
      const data = new FormData(e.target);
      await fetch('/submit',{method:'POST',body:data});
    });
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(TEMPLATE)

@app.route('/status')
def status():
    return jsonify(scheduler.get_status())

@app.route('/submit', methods=['POST'])
def submit():
    gpu = int(request.form.get('gpu', 1))
    mem = int(request.form.get('mem', 4))
    runtime = int(request.form.get('runtime', random.randint(5, 15)))
    job = Job(random_job_id(), gpu, mem, runtime)
    scheduler.submit_job(job)
    return jsonify({"message": f"Job {job.job_id} submitted."})

if __name__ == "__main__":
    app.run(debug=True)
