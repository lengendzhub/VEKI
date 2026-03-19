up:
docker compose -f ../infra/docker-compose.yml up -d

down:
docker compose -f ../infra/docker-compose.yml down

logs:
docker compose -f ../infra/docker-compose.yml logs -f backend

logs-worker:
docker compose -f ../infra/docker-compose.yml logs -f worker

test:
pytest tests/ -v --tb=short

test-cov:
pytest tests/ --cov=app --cov-report=html

migrate:
alembic upgrade head

rollback:
alembic downgrade -1

kill-switch:
curl -X POST http://localhost:8000/api/v1/strategy/kill-switch \
  -H "Authorization: Bearer $(ADMIN_TOKEN)" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Manual emergency stop via Makefile"}'

kill-switch-reset:
curl -X POST http://localhost:8000/api/v1/strategy/kill-switch/reset \
  -H "Authorization: Bearer $(ADMIN_TOKEN)"

metrics:
curl -H "X-Internal-Key: $(INTERNAL_KEY)" http://localhost:8000/api/v1/metrics | python3 -m json.tool
