#!/bin/bash

docker run \
  -d \
  --name haproxy \
  --net host \
  -v `pwd`/../etc/haproxy:/usr/local/etc/haproxy:ro \
  haproxy:alpine
