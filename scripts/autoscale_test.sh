#!/bin/bash
# 10-minute HPA test: 2 min @10, 5 min @100, 3 min @10 req/s
cd "$(dirname "$0")/.."
mkdir -p results
kubectl scale deployment emi-web --replicas=1 -n emi
kubectl rollout status deployment/emi-web -n emi
kubectl apply -f k8s/hpa/hpa.yaml
sleep 30
python3 scripts/profile.py --out results/autoscale --duration 620 --hpa &
PP=$!
python3 scripts/loadgen.py --url http://emi.local/ --phases 10:120,100:300,10:180 \
    --out results/autoscale_requests.csv
wait $PP
