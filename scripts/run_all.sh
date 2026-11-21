#!/bin/bash
# 15 runs: replicas 1,2,3 x rates 10,25,50,100,200  (60 s each). Takes ~40 minutes.
cd "$(dirname "$0")/.."
mkdir -p results
kubectl delete hpa emi-web -n emi --ignore-not-found
echo "replicas,rate,avg_ms,errors,total" > results/summary.csv
for R in 1 2 3; do
  kubectl scale deployment emi-web --replicas=$R -n emi
  kubectl rollout status deployment/emi-web -n emi
  sleep 20
  for RATE in 10 25 50 100 200; do
    TAG=r${R}_rate${RATE}
    echo "=== replicas=$R rate=$RATE ==="
    python3 scripts/profile.py --out results/$TAG --duration 65 &
    PP=$!
    python3 scripts/loadgen.py --url http://emi.local/ --phases ${RATE}:60 \
        --out results/${TAG}_requests.csv --summary results/summary.csv --label "$R,$RATE"
    wait $PP
    sleep 20
  done
done
