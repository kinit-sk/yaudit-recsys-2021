#! /bin/bash

sudo docker run -d --name='chrome' -p 4444:4444 --shm-size 14g selenium/standalone-chrome
