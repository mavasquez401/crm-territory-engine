"""
Deduplication Pipeline Module

Orchestrates the deduplication process:
1. Identify potential duplicates using fuzzy matching
2. Merge duplicate records based on rules
3. Generate deduplication reports
"""

from typing import Dict, List, Optional
from pathlib import Path
import pandas as pd
import logging

from python_etl.dedupe.fuzzy_matcher import find_duplicates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def identify_duplicates(
    df: pd.DataFrame,
    threshold: float = 85.0,
    name_column: str = "client_name",
    id_column: str = "client_id"
) -> List[Dict]:
    """
    Identify potential duplicate records in the dataset.
    
    Args:
        df: DataFrame containing client records
        threshold: Similarity threshold for duplicate detection
        name_column: Column containing client names
        id_column: Column containing client IDs
        
    Returns:
        List of duplicate pairs with similarity scores
    """
    logger.info("Starting duplicate identification")
    
    # Find duplicates using fuzzy matching
    duplicates = find_duplicates(
        df,
        name_column=name_column,
        id_column=id_column,
        threshold=threshold
    )
    
    logger.info(f"Identified {len(duplicates)} potential duplicate pairs")
    
    return duplicates


def merge_duplicates(
    df: pd.DataFrame,
    duplicates: List[Dict],
    id_column: str = "client_id",
    merge_strategy: str = "most_complete"
) -> pd.DataFrame:
    """
    Merge duplicate records based on specified strategy.
    
    Args:
        df: DataFrame containing client records
        duplicates: List of duplicate pairs
        id_column: Column containing client IDs
        merge_strategy: Strategy for merging duplicates:
            - "most_complete": Keep record with most non-null values
            - "first": Keep first occurrence
            - "manual": Flag for manual review (no automatic merge)
            
    Returns:
        DataFrame with duplicates merged
    """
    logger.info(f"Merging duplicates using strategy: {merge_strategy}")
    
    if merge_strategy == "manual":
        logger.info("Manual merge strategy - no automatic merging performed")
        return df
    
    # Track IDs to remove
    ids_to_remove = set()
    
    # Process each duplicate pair
    for dup in duplicates:
        id1 = dup["id1"]
        id2 = dup["id2"]
        
        # Skip if already processed
        if id1 in ids_to_remove or id2 in ids_to_remove:
            continue
        
        # Get records
        record1 = df[df[id_column] == id1].iloc[0]
        record2 = df[df[id_column] == id2].iloc[0]
        
        # Determine which to keep based on strategy
        if merge_strategy == "most_complete":
            # Count non-null values
            non_null_count1 = record1.notna().sum()
            non_null_count2 = record2.notna().sum()
            
            if non_null_count1 >= non_null_count2:
                ids_to_remove.add(id2)
                logger.debug(f"Keeping ID {id1}, removing ID {id2}")
            else:
                ids_to_remove.add(id1)
                logger.debug(f"Keeping ID {id2}, removing ID {id1}")
                
        elif merge_strategy == "first":
            # Keep first occurrence (lower ID)
            ids_to_remove.add(id2)
            logger.debug(f"Keeping ID {id1}, removing ID {id2}")
    
    # Remove duplicate records
    df_deduped = df[~df[id_column].isin(ids_to_remove)].copy()
    
    removed_count = len(ids_to_remove)
    logger.info(f"Removed {removed_count} duplicate records")
    logger.info(f"Final record count: {len(df_deduped)}")
    
    return df_deduped


def generate_deduplication_report(
    duplicates: List[Dict],
    output_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Generate a detailed report of identified duplicates.
    
    Args:
        duplicates: List of duplicate pairs
        output_path: Optional path to save report CSV
        
    Returns:
        DataFrame containing duplicate report
    """
    logger.info("Generating deduplication report")
    
    if not duplicates:
        logger.info("No duplicates found - empty report")
        return pd.DataFrame()
    
    # Convert to DataFrame
    report_df = pd.DataFrame(duplicates)
    
    # Add summary statistics
    total_pairs = len(duplicates)
    high_confidence = len([d for d in duplicates if d["confidence"] == "HIGH"])
    medium_confidence = len([d for d in duplicates if d["confidence"] == "MEDIUM"])
    low_confidence = len([d for d in duplicates if d["confidence"] == "LOW"])
    
    logger.info(f"Duplicate Summary:")
    logger.info(f"  Total pairs: {total_pairs}")
    logger.info(f"  HIGH confidence: {high_confidence}")
    logger.info(f"  MEDIUM confidence: {medium_confidence}")
    logger.info(f"  LOW confidence: {low_confidence}")
    
    # Save to file if path provided
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        report_df.to_csv(output_path, index=False)
        logger.info(f"Report saved to: {output_path}")
    
    return report_df


def run_deduplication_pipeline(
    df: pd.DataFrame,
    threshold: float = 85.0,
    merge_strategy: str = "most_complete",
    report_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Run complete deduplication pipeline.
    
    Args:
        df: DataFrame containing client records
        threshold: Similarity threshold for duplicate detection
        merge_strategy: Strategy for merging duplicates
        report_path: Optional path to save deduplication report
        
    Returns:
        Deduplicated DataFrame
    """
    logger.info("Starting deduplication pipeline")
    
    # Step 1: Identify duplicates
    duplicates = identify_duplicates(df, threshold=threshold)
    
    # Step 2: Generate report
    if duplicates:
        generate_deduplication_report(duplicates, output_path=report_path)
    
    # Step 3: Merge duplicates
    df_deduped = merge_duplicates(df, duplicates, merge_strategy=merge_strategy)
    
    logger.info("Deduplication pipeline complete")
    
    return df_deduped

