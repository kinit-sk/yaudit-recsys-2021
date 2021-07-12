#! /bin/bash

for run in {1..10}; do
	sudo docker container logs -f yaudit_run_account_$run &> docker_logs/account_$run.log
done
