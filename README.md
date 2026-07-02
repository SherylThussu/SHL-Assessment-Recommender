# SHL Assessment Recommender

A FastAPI-based conversational recommender for SHL assessments. The service accepts stateless conversation history and returns the next assistant reply plus a structured shortlist of SHL catalog recommendations when enough context is available.

## Endpoints

### Health Check

```http
GET /health