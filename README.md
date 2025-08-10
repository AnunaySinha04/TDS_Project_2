# Data Analyst Agent (FastAPI)

POST `/api/` with multipart form:
- `questions.txt` (required)
- optional files (`data.csv`, `image.png`, ...)

Responses returned as JSON or base64 image strings as required.

See `.env.example` for configuration. Start with:
`./run_local.sh`
