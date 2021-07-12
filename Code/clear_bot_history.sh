#! /bin/bash

for run in {1..10}; do
	sudo docker run -d --net=host --env-file ./.env -e YAUDIT_ACCOUNT_ID=$run -e CHROME_PORT=4444 -v ~/yaudit:/app --name='yaudit_clear_history_account_'$run --entrypoint '/bin/bash' selenium_bot:latest -c 'python3 clear_history.py'
	sleep 15
done
