#!/bin/bash

set -e

while [ 0 ]; do
    echo -n "Average time per request: "
    echo `ab -n 10 -c $1 http://localhost:7000/ |grep 'Time per request.*mean)'|awk '{ print $4 }'` ms
done