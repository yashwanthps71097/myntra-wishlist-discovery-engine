import argparse
import sys
import logging
from ingest.pipeline import IngestionPipeline

# Set up logging format
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("run_ingestion")

def main():
    parser = argparse.ArgumentParser(description="AI Discovery Engine Ingestion Script - Phase 1")
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max number of items to fetch per data source (default: 50)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom output directory to save raw feedback data"
    )
    
    args = parser.parse_args()
    
    logger.info("Initializing Ingestion Pipeline...")
    pipeline = IngestionPipeline(output_dir=args.output_dir)
    
    try:
        output_file = pipeline.run(limit_per_source=args.limit)
        logger.info(f"Ingestion completed successfully! Dataset saved at: {output_file}")
    except Exception as e:
        logger.error(f"Ingestion pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
