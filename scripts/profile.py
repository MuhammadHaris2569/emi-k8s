#!/usr/bin/env python3
"""Saves host CPU (every 1 s) and kubectl top pods (every 15 s) to CSV with timestamps.
Usage: python3 scripts/profile.py --out results/r3_rate100 --duration 65 [--hpa]"""
import argparse, csv, re, subprocess, threading, time

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

def cpu_times():
    v = list(map(int, open('/proc/stat').readline().split()[1:]))
    return v[3] + v[4], sum(v)

def host_loop(path, stop):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['timestamp', 'host_cpu_percent'])
        pi, pt = cpu_times()
        while not stop.is_set():
            time.sleep(1)
            i, t = cpu_times()
            w.writerow([int(time.time()), round(100 * (1 - (i - pi) / max(t - pt, 1)), 1)])
            f.flush(); pi, pt = i, t

def pods_loop(path, stop):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['timestamp', 'pod', 'cpu_millicores', 'memory_Mi'])
        while not stop.is_set():
            ts = int(time.time())
            for line in sh('kubectl top pods -n emi --no-headers').splitlines():
                p = line.split()
                if len(p) >= 3:
                    w.writerow([ts, p[0], p[1].rstrip('m'), p[2].rstrip('Mi')])
            f.flush(); stop.wait(15)

def hpa_loop(path, stop):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['timestamp', 'cpu_percent', 'target_percent', 'replicas'])
        while not stop.is_set():
            out = sh('kubectl get hpa emi-web -n emi --no-headers')
            m = re.search(r'(\d+)%/(\d+)%\s+\d+\s+\d+\s+(\d+)', out)
            if m: w.writerow([int(time.time()), m.group(1), m.group(2), m.group(3)])
            f.flush(); stop.wait(15)

ap = argparse.ArgumentParser()
ap.add_argument('--out', required=True)
ap.add_argument('--duration', type=int, required=True)
ap.add_argument('--hpa', action='store_true')
a = ap.parse_args()

stop = threading.Event()
targets = [(host_loop, a.out + '_host.csv'), (pods_loop, a.out + '_pods.csv')]
if a.hpa: targets.append((hpa_loop, a.out + '_hpa.csv'))
ths = [threading.Thread(target=fn, args=(p, stop)) for fn, p in targets]
[t.start() for t in ths]
time.sleep(a.duration)
stop.set()
[t.join() for t in ths]
