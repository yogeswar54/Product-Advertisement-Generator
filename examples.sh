#!/usr/bin/env sh
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:8000/personas
curl -s http://127.0.0.1:8000/personas/college_students
curl -s -X POST http://127.0.0.1:8000/inputs/validate -H 'Content-Type: application/json' --data @schemas/examples/input.example.json
curl -s -X POST http://127.0.0.1:8000/audiences/profile -H 'Content-Type: application/json' -d '{"persona_id":"college_students"}'
