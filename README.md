# Loan EMI Calculator on Kubernetes (Minikube)

Node.js/Express + jQuery/Bootstrap app, MongoDB 3-member replica set (StatefulSet), NGINX Ingress, HPA.

## Bring up on a fresh Minikube
```bash
minikube start --driver=docker --cpus=2 --memory=3500
minikube addons enable ingress
minikube addons enable metrics-server
docker build -t emi-web:1.0 ./app
minikube image load emi-web:1.0
kubectl apply -f k8s/
kubectl get pods -n emi -w        # wait until all Running/Ready
echo "$(minikube ip) emi.local" | sudo tee -a /etc/hosts
# open http://emi.local
```
## Experiments
- `bash scripts/count_requests.sh 30` - requests served per pod
- `bash scripts/request_loop.sh 300` - failure check during rolling update
- `bash scripts/run_all.sh` - 15 load-test runs -> results/summary.csv
- `bash scripts/autoscale_test.sh` - HPA test (applies k8s/hpa/hpa.yaml)
- `python3 scripts/plot.py` - graphs
