#!/bin/bash

[[ -z "${WORKERS_NUM}" ]] && WORKERS='1' || WORKERS="${WORKERS_NUM}"

echo Starting bjoern wsgi server with $WORKERS workers.

for i in `seq $WORKERS`
do
  python ./serve_bjoern.py &
done

tail -F -n0 /dev/null
