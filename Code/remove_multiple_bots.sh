#! /bin/bash

for run in {1..10}; do
	sudo docker container stop yaudit_run_account_$run
	sudo docker rm yaudit_run_account_$run
	sleep 1
done
