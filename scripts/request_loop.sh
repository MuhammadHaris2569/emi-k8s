#!/bin/bash
# Usage: bash scripts/request_loop.sh 300   (300 requests, ~5 per second)
N=${1:-300}
mkdir -p results
LOG=results/request_loop.log
: > $LOG
for i in $(seq 1 $N); do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 -X POST http://emi.local/api/emi \
    -H 'Content-Type: application/json' -d '{"principal":500000,"rate":12,"months":24}')
  echo "$(date +%T) $i $CODE" | tee -a $LOG
  sleep 0.2
done
echo "TOTAL: $N   FAILED: $(grep -vc ' 200$' $LOG)" | tee -a $LOG
