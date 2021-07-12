#! /bin/bash

for run in {1..10}; do
	sudo docker container stop chrome_$run
	sudo docker rm chrome_$run
	sleep 1
done
