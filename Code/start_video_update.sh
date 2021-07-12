#! /bin/bash

sudo docker run -d --name=yaudit_video_update --net=host --env-file ./.env -v ~/yaudit:/app --entrypoint '/bin/bash' selenium_bot -c 'python3 -m scripts.update_stats'
