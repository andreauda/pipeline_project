📦 End-to-End Data Pipeline
API Ingestion • Transformation • Airflow Orchestration

🎯 1. Objective
Build an end-to-end data pipeline simulating a real-world system (e.g. CRM/ERP), including:

Data ingestion from external APIs
Raw data persistence
Data transformation and validation
Loading into analytical storage
Automated orchestration with Apache Airflow


🏗️ 2. Architecture
API → Ingestion → Raw Layer → Transformation → Processed Layer → Load → BI / Analytics


🔹 2.1 Ingestion Layer
🎯 Responsibilities

Fetch data from external APIs
Handle retries, timeouts and rate limiting
Validate API responses
Store raw data (no transformation)
Log all operations


📄 config.yaml
Declarative configuration file (no code execution)
Purpose:

Easy to modify without changing Python code
Centralized control of pipeline settings

Contains:

API configuration
Endpoints (users, posts, comments, etc.)
Retry strategy (5xx errors)
Rate limiting (429)
Logging settings


⚙️ config.py
Responsibilities:

Load config.yaml into Python (dict)
Validate structure and required keys
Handle YAML parsing errors

Design principles:

No logging (kept in orchestration layer)
Defensive programming


🌐 client.py
Reusable HTTP client
✅ Responsibilities

Perform API requests
Handle retry logic (5xx errors)
Exponential backoff
Rate limit handling (429)
Timeout control
Prevent infinite retry loops
Session reuse (requests.Session)

❌ Not responsible for

Logging → handled in ingest.py
Authentication → not needed (JSONPlaceholder)
Pagination → would be handled in orchestrator


🧠 ingest.py
Main ingestion orchestrator
Responsibilities:

Load configuration
Initialize logging
Iterate through endpoints
Call API via client.py
Validate response format
Save raw data (JSONL)
Log execution details and performance


💾 Raw Data Layer
Structure:
data/raw/<endpoint>/<date_timestamp>.jsonl

Example:
data/raw/users/2026-05-08_164459.jsonl

Format:

JSON Lines (.jsonl)
One record per line
Optimized for streaming and scalability


🔹 2.2 Transformation Layer
📄 transform.py
Transforms raw data into structured datasets
Responsibilities:

JSON parsing
Flatten nested structures (typical in CRM data)
Data cleaning:

Null handling
Deduplication
Type casting


Data quality checks
Schema validation
KPI computation
Splitting into:

Fact tables
Dimension tables




🔹 2.3 Load Layer
📄 load.py
Loads processed data into storage systems
Responsibilities:

Create database tables
Insert / upsert data
Support databases:

SQLite (local dev)
PostgreSQL / MySQL (production)


Prepare data for BI tools (e.g. Tableau)


🔹 2.4 Orchestration
📄 pipeline_dag.py

Airflow DAG for pipeline scheduling
Runs ingestion → transformation → load
Supports retries and monitoring

🐳 Docker

Used to run Airflow environment

✅ Key Features
🔁 Idempotency

Re-running the pipeline does not duplicate data

📊 Observability

Centralized logging
Execution time tracking
Error logging per endpoint

⚙️ Config-Driven Design

Pipeline behavior controlled via config.yaml

📦 Modular Architecture

Clear separation of concerns:

ingestion
transformation
load



