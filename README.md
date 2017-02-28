BGG Graph
=========

Uses the [BoardGameGeek API](https://boardgamegeek.com/wiki/page/BGG_XML_API2) to generate board game decision flowcharts

Getting started
---------------
1. [Install Docker Compose](https://docs.docker.com/compose/install/)
2. `docker-compose up`
3. Open http://localhost:8000

FAQ
---
* How do I reload Celery code changes
  - `docker-compose exec celery ./restart-worker.sh` will do it. Django changes will just get auto-reloaded.