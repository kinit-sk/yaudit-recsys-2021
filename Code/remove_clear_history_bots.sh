#! /bin/bash

for run in {1..10}; do
	sudo docker container stop yaudit_clear_history_account_$run
	sudo docker rm yaudit_clear_history_account_$run
	sleep 1
done
