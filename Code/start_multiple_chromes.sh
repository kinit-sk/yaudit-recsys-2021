#! /bin/bash

for run in {1..10}; do
  sudo docker run -d --name='chrome_'$run -p $((4443+$run)):4444 --shm-size 2g selenium/standalone-chrome
done
