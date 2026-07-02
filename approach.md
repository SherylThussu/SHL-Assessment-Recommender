# Approach: SHL Assessment Recommender

## Problem Understanding

The task is to build a stateless conversational agent that recommends SHL assessments from the SHL Individual Test Solutions catalog. The agent must clarify vague requests, recommend 1 to 10 catalog-grounded assessments, refine recommendations when the user changes constraints, compare assessments using catalog data, and refuse off-topic, legal, or prompt-injection requests.

The most important hard constraints are schema compliance, catalog-only recommendations, no hallucinated URLs, and completing conversations within the turn and timeout limits.

## Data Preparation

I used the provided SHL catalog export as the source of truth. The raw file was stored as `data/raw/catalog.html`. Although the file is HTML, the useful catalog data is embedded as JSON inside a `<pre>` block. I wrote `app/catalog_loader.py` to extract that JSON, clean broken newlines inside strings, normalize names, decode HTML entities, infer SHL test type codes, and save the cleaned result as `data/catalog.json`.

Each catalog item keeps the fields needed for retrieval and response grounding: name, URL, test type, keys, description, duration, languages, job levels, remote flag, and adaptive flag. The API only returns recommendation names and URLs from this cleaned catalog.

## System Design

The service is implemented with FastAPI and exposes two endpoints:

- `GET /health` returns `{"status": "ok"}`.
- `POST /chat` accepts full stateless message history and returns `reply`, `recommendations`, and `end_of_conversation`.

The agent does not store conversation state. Every decision is made from the full `messages` array sent in the request.

The recommendation logic has two layers. First, it detects high-confidence role patterns from the public traces, such as graduate finance analysts, Java backend engineers, contact center agents, safety-critical plant operators, sales reskilling, and graduate management trainees. These map to curated catalog item names. Second, it has a keyword scoring fallback over the full catalog for unseen queries. This fallback scores matches across name, description, keys, and job levels.

This design is intentionally simple and explainable. I avoided relying on a generative model for recommendations because the assignment strongly penalizes hallucinated assessments and invalid URLs.

## Conversation Behavior

For vague requests such as “I need an assessment,” the agent asks for role, seniority, skills, language, or time constraints instead of recommending too early.

For recommendation-ready requests, the agent returns a shortlist of 1 to 10 assessments. Each recommendation follows the required schema with `name`, `url`, and `test_type`.

For refinement, the agent reads the full conversation history, so later user constraints such as adding simulations, adding AWS/Docker, or dropping OPQ update the selected shortlist.

For comparison questions, the agent detects phrases such as “difference between” or “compare,” identifies catalog items through aliases, and builds a grounded comparison using catalog fields like description, duration, and test type. It returns no recommendations for comparison-only turns.

## Guardrails

The guardrail layer refuses legal questions, general hiring advice, off-topic requests, and prompt-injection attempts. For example, a HIPAA legal compliance question is refused, while a catalog-grounded explanation of what the HIPAA assessment measures remains allowed.

Every recommendation is looked up from `data/catalog.json`, so the system does not invent SHL product names or URLs.

## Evaluation

I used the 10 public conversation traces to identify expected behaviors and common target shortlists. I also created automated tests with FastAPI’s `TestClient`.

The current tests cover:

- `/health`
- vague-query clarification
- legal/off-topic refusal
- finance graduate recommendations
- Java backend/cloud recommendations
- strict recommendation schema
- catalog-grounded comparison behavior

The latest local test result was 7 passing tests. During development, I improved the system after finding that comparison behavior was not initially handled. Adding comparison detection and catalog-grounded replies improved alignment with the assignment’s behavior probes.

## What Did Not Work

A purely generic keyword search was not enough for the public traces because some role descriptions imply specific SHL assessment combinations. For example, senior leadership selection requires OPQ32r plus leadership-related reports, and contact center screening depends on spoken English variant and simulation products. I therefore added a curated pattern layer before the keyword fallback.

I also avoided a fully LLM-driven approach. It would be more conversational, but it increases the risk of hallucinated products, invalid URLs, slower responses, and harder-to-debug behavior under automated replay.

## AI Tool Usage

I used AI assistance to understand the assignment, structure the implementation, identify edge cases from the public traces, and draft code/tests. I reviewed the logic and tested it locally to ensure I understood the design and could explain the trade-offs.