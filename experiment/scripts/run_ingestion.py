import argparse
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from ingestion import run_experiment_ingestion

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="실험용 ingestion 파이프라인 실행")
    parser.add_argument(
        "--config", type=str, required=True, help="실험 config 파일 경로"
    )
    args = parser.parse_args()
    run_experiment_ingestion(args.config)
