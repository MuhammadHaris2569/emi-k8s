#!/bin/bash
# Usage: bash scripts/count_requests.sh 30
N=${1:-30}
for i in $(seq 1 $N); do
  curl -s -X POST http://emi.local/api/emi -H 'Content-Type: application/json' \
    -d '{"principal":500000,"rate":12,"months":24}' | grep -o '"servedBy":"[^"]*"'
done | sort | uniq -c
