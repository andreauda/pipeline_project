import logging
from typing import Any, Dict, List
import time
import json
from datetime import datetime
from pathlib import Path

from ingestion.config import load_config
from ingestion.client import APIClient
from common.logging_config import setup_logging
from common.path import PROJECT_ROOT, RAW_DATA_PATH

# =========================
# RAW STORAGE HELPERS
# =========================
def build_raw_path(endpoint_name: str) -> Path:
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%H%M%S")

    endpoint_name = endpoint_name.strip("/").replace("/", "_")

    dir_path = RAW_DATA_PATH / endpoint_name
    dir_path.mkdir(parents=True, exist_ok=True)

    return dir_path / f"{today}_{timestamp}.jsonl"

def write_jsonl(file_path: Path, data: List[Dict[str, Any]]) -> None:
    with open(file_path, "w", encoding="utf-8") as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

# =========================
# MAIN PIPELINE
# =========================
def run_ingestion() -> Dict[str, List[Dict[str, Any]]]:
    # Load config
    config = load_config()

    # Setup logging
    setup_logging(config)
    logger = logging.getLogger("pipeline.ingest")
    
    logger.info(f"Loaded config from {config.get('_config_path', 'unknown')}")

    logger.info("Ingestion pipeline started")

    # Init client
    client = APIClient(config)

    # Fetch endpoints
    endpoints = config["ingestion"]["endpoints"]

    results: Dict[str, List[Dict[str, Any]]] = {}

    for endpoint in endpoints:
        logger.info(f"Fetching data from {endpoint}")

        start_time = time.time()

        try:
            response = client.get(endpoint)
        except Exception as exc:
            duration = time.time() - start_time
            logger.error(f"{endpoint} - Request failed after {duration:.2f}s: {exc}")
            continue

        duration = time.time() - start_time
        logger.info(f"{endpoint} - Request completed in {duration:.2f}s")

        # =========================
        # RESPONSE HANDLING
        # =========================
        if isinstance(response, dict):
            items = response.get("data")
        else:
            items = response

        if items is None:
            logger.error(f"{endpoint} - Missing 'data' field in response")
            continue

        if not isinstance(items, list):
            logger.error(f"{endpoint} - Invalid response format (expected list)")
            continue

        if len(items) == 0:
            logger.warning(f"{endpoint} - No data returned")
            results[endpoint] = []
            continue

        # =========================
        # STORE RESULTS
        # =========================
        results[endpoint] = items

        file_path = build_raw_path(endpoint)
        write_jsonl(file_path, items)

        logger.info(
            f"{endpoint} - Saved {len(items)} records to {file_path.relative_to(PROJECT_ROOT)}"
        )

    logger.info("Ingestion pipeline completed")

    return results


if __name__ == "__main__":
    run_ingestion()