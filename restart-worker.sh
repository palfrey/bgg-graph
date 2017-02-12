#!/bin/bash
kill -HUP $(cat /var/run/celery-worker.pid)