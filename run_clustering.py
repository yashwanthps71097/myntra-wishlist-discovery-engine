import os
import json
import logging
import sys
import argparse
from ingest.processing.embeddings import EmbeddingGenerator
from ingest.processing.clustering import FeedbackClustering

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("run_clustering")

def main():
    parser = argparse.ArgumentParser(description="AI Discovery Engine Clustering Script - Phase 2")
    parser.add_argument(
        "--input-file",
        type=str,
        default="data/raw/raw_feedback.json",
        help="Path to raw sanitized feedback json file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/processed",
        help="Directory to save the processed clustered data"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        logger.error(f"Input file not found: {args.input_file}. Please run Phase 1 Ingestion first.")
        sys.exit(1)
        
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 1. Load data
    logger.info(f"Loading raw sanitized feedback from {args.input_file}...")
    with open(args.input_file, "r", encoding="utf-8") as f:
        records = json.load(f)
        
    if not records:
        logger.warning("No records found in raw input file. Exiting.")
        return

    # Extract texts
    texts = [r.get("text", "") for r in records]
    
    # 2. Generate Embeddings
    logger.info("Initializing embedding generation...")
    embedder = EmbeddingGenerator()
    embeddings = embedder.generate(texts)
    
    # 3. Fit Clusters
    logger.info("Initializing cluster grouping...")
    clustering = FeedbackClustering(min_cluster_size=2)
    labels, keywords_map = clustering.fit_predict(embeddings, texts)
    
    # 4. Enrich records
    logger.info("Enriching records with cluster IDs and keywords...")
    for idx, record in enumerate(records):
        cluster_id = labels[idx]
        record["cluster_id"] = cluster_id
        record["cluster_keywords"] = keywords_map.get(cluster_id, ["General"])
        
    # Write output
    output_file = os.path.join(args.output_dir, "clustered_feedback.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=4, ensure_ascii=False)
        
    logger.info(f"Clustering complete!")
    logger.info(f"Unique clusters identified: {len(set(labels)) - (1 if -1 in labels else 0)}")
    logger.info(f"Clustered dataset successfully saved to: {output_file}")

if __name__ == "__main__":
    main()
