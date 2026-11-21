#!/usr/bin/env python3
"""Makes Graph 1, 2, 3 from the files in results/.  Needs: matplotlib"""
import csv, collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---- Graph 1
rows = list(csv.DictReader(open('results/summary.csv')))
plt.figure(figsize=(7, 4.5))
for R in sorted({r['replicas'] for r in rows}):
    pts = sorted((int(r['rate']), float(r['avg_ms'])) for r in rows if r['replicas'] == R)
    plt.plot([p[0] for p in pts], [p[1] for p in pts], marker='o', label=f'{R} replica(s)')
plt.xlabel('Request rate (req/s)'); plt.ylabel('Average response time (ms)')
plt.title('Graph 1: Response time vs request rate'); plt.grid(True); plt.legend()
plt.savefig('results/graph1_response_time.png', dpi=150, bbox_inches='tight')

# ---- Graph 2  (CPU % of the 250m limit)
data = collections.defaultdict(list)
for r in csv.DictReader(open('results/r3_rate100_pods.csv')):
    if r['pod'].startswith('emi-web'):
        data[r['pod']].append((int(r['timestamp']), float(r['cpu_millicores']) / 250 * 100))
t0 = min(t for v in data.values() for t, _ in v)
plt.figure(figsize=(7, 4.5))
for pod, v in data.items():
    plt.plot([t - t0 for t, _ in v], [c for _, c in v], marker='o', label=pod[-11:])
plt.xlabel('Time (s)'); plt.ylabel('CPU (% of 250m limit)')
plt.title('Graph 2: Per-pod CPU, 100 req/s, 3 replicas'); plt.grid(True); plt.legend()
plt.savefig('results/graph2_pod_cpu.png', dpi=150, bbox_inches='tight')

# ---- Graph 3
hpa = list(csv.DictReader(open('results/autoscale_hpa.csv')))
reqs = list(csv.DictReader(open('results/autoscale_requests.csv')))
t0 = min(float(r['timestamp']) for r in reqs)
bins = collections.Counter(int((float(r['timestamp']) - t0) // 15) for r in reqs)
bx = sorted(bins)
fig, ax = plt.subplots(3, 1, sharex=True, figsize=(8, 8))
ax[0].step([b * 15 for b in bx], [bins[b] / 15 for b in bx], where='post')
ax[0].set_ylabel('Request rate (req/s)')
ax[1].plot([int(r['timestamp']) - t0 for r in hpa], [float(r['cpu_percent']) for r in hpa], marker='o')
ax[1].axhline(50, color='red', ls='--', label='target 50%'); ax[1].legend()
ax[1].set_ylabel('Avg CPU utilization (%)')
ax[2].step([int(r['timestamp']) - t0 for r in hpa], [int(r['replicas']) for r in hpa], where='post')
ax[2].set_ylabel('Web replicas'); ax[2].set_xlabel('Time (s)')
for a in ax: a.grid(True)
fig.suptitle('Graph 3: Autoscaling test')
plt.savefig('results/graph3_autoscaling.png', dpi=150, bbox_inches='tight')
print('Saved graphs in results/')
