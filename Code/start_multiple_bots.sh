#! /bin/bash

for run in {1..10}; do
	sudo docker container start yaudit_run_account_$run
	sleep 1
done
