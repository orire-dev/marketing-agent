#!/bin/bash
# Example API call to generate creative

curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d @example_request.json | jq '.'
