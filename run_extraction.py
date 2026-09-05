import os
import json
import logging
import sys
import argparse
from ingest.processing.database import DatabaseManager
from ingest.processing.extractor import GroqExtractor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("run_extraction")

def main():
    parser = argparse.ArgumentParser(description="AI Discovery Engine Extraction Script - Phase 3")
    parser.add_argument(
        "--input-file",
        type=str,
        default="data/processed/clustered_feedback.json",
        help="Path to processed clustered feedback JSON file"
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="discovery.db",
        help="Path to SQLite database file"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of comments to process via LLM (optional)"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        logger.error(f"Input file not found: {args.input_file}. Please run Phase 2 Clustering first.")
        sys.exit(1)
        
    db = DatabaseManager(db_path=args.db_path)
    
    # 1. Load clustered data and save comments to SQLite
    logger.info(f"Loading clustered feedback from {args.input_file}...")
    with open(args.input_file, "r", encoding="utf-8") as f:
        records = json.load(f)
        
    logger.info(f"Syncing {len(records)} comments to the local SQLite database...")
    for record in records:
        db.save_comment(record)
        
    # 2. Get unprocessed comments
    unprocessed = db.get_unprocessed_comments()
    logger.info(f"Found {len(unprocessed)} unprocessed records to analyze.")
    
    if not unprocessed:
        logger.info("All comments have already been processed. No extraction required.")
        print_summary(db)
        return

    # Apply process limit if set
    if args.limit:
        unprocessed = unprocessed[:args.limit]
        logger.info(f"Limiting execution to first {args.limit} unprocessed items.")

    # 3. Process each comment via LLM
    extractor = GroqExtractor()
    logger.info("Beginning batch structured extraction via LLM/Heuristics...")
    
    success_count = 0
    for idx, (cid, text, cluster_id) in enumerate(unprocessed):
        logger.info(f"[{idx+1}/{len(unprocessed)}] Processing comment ID {cid}...")
        extracted_data = extractor.extract(text)
        
        # Save structured extraction
        db.save_extraction(cid, extracted_data)
        success_count += 1
        
    logger.info(f"Successfully processed and stored {success_count} structured extractions.")
    
    # Print results summary
    print_summary(db)

def print_summary(db):
    print("\n" + "="*50)
    print("           EXTRACTION BARRIER SUMMARY")
    print("="*50)
    summary = db.get_extraction_summary()
    print(f"{'Primary Barrier':<25} | {'Frequency':<10} | {'Avg Intensity':<12}")
    print("-"*50)
    for barrier, freq, avg_int in summary:
        print(f"{barrier:<25} | {freq:<10} | {avg_int:<12.1f}")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
