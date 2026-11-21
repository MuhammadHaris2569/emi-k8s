#!/usr/bin/env python3
"""Open-loop load generator: random valid POST /api/emi at a fixed rate.
Usage: python3 scripts/loadgen.py --url http://emi.local/ --phases 100:60 --out results/x.csv
       --phases is rate:seconds[,rate:seconds...]  e.g. 10:120,100:300,10:180"""
import argparse, csv, json, random, time, urllib.request, urllib.error
import concurrent.futures as cf

def one(url):
    body = json.dumps({"principal": random.randint(10000, 2000000),
                       "rate": round(random.uniform(5, 25), 2),
                       "months": random.randint(6, 120)}).encode()
    req = urllib.request.Request(url.rstrip('/') + '/api/emi', data=body,
                                 headers={'Content-Type': 'application/json'})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            r.read(); st = r.status
    except urllib.error.HTTPError as e:
        st = e.code
    except Exception:
        st = 0
    return t0, (time.time() - t0) * 1000, st

ap = argparse.ArgumentParser()
ap.add_argument('--url', default='http://emi.local/')
ap.add_argument('--phases', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--summary')
ap.add_argument('--label', default='')
a = ap.parse_args()

phases = [tuple(int(x) for x in p.split(':')) for p in a.phases.split(',')]
pool = cf.ThreadPoolExecutor(max_workers=400)
futs, t = [], time.time()
for rate, secs in phases:
    for i in range(rate * secs):
        d = t + i / rate - time.time()
        if d > 0: time.sleep(d)
        futs.append(pool.submit(one, a.url))
    t += secs
res = [f.result() for f in futs]

with open(a.out, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['timestamp', 'latency_ms', 'status'])
    w.writerows([(round(x[0], 3), round(x[1], 1), x[2]) for x in res])

avg = sum(x[1] for x in res) / len(res)
err = sum(1 for x in res if x[2] != 200)
print(f"requests={len(res)} avg_ms={avg:.1f} errors={err}")
if a.summary:
    with open(a.summary, 'a') as f:
        f.write(f"{a.label},{avg:.1f},{err},{len(res)}\n")
