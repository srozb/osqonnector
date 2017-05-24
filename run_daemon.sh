#!/bin/bash

docker run \
  -d \
  -e "WORKERS_NUM=2" \
  -v `pwd`/:/usr/src/app/osqonnector \
  -v `pwd`/../db:/usr/src/app/db \
  --name osqonnector \
  --net host \
  srozb/osqonnector
