"""
Fuzzy Matching Module

Uses rapidfuzz library to find similar client names and identify potential duplicates.
Configurable similarity threshold allows tuning of matching sensitivity.
"""

from typing import List, Tuple, Dict
import pandas as pd
from rapidfuzz import fuzz, process
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_similarity(str1: str, str2: str, method: str = "token_sort_ratio") -> float:
    """
    Calculate similarity score between two strings.
    
    Args:
        str1: First string
        str2: Second string
        method: Matching method to use (default: token_sort_ratio)
            - "ratio": Simple character-by-character comparison
            - "token_sort_ratio": Tokenize and sort before comparison (handles word order)
            - "token_set_ratio": Tokenize and compare unique tokens
            
    Returns:
        Similarity score between 0 and 100
    """
    # Handle empty or null strings
    if not str1 or not str2 or pd.isna(str1) or pd.isna(str2):
        return 0.0
    
    # Convert to strings and normalize
    str1 = str(str1).strip().lower()
    str2 = str(str2).strip().lower()
    
    # Calculate similarity based on method
    if method == "ratio":
        return fuzz.ratio(str1, str2)
    elif method == "token_sort_ratio":
        return fuzz.token_sort_ratio(str1, str2)
    elif method == "token_set_ratio":
        return fuzz.token_set_ratio(str1, str2)
    else:
        raise ValueError(f"Unknown matching method: {method}")


def find_duplicates(
    df: pd.DataFrame,
    name_column: str = "client_name",
    id_column: str = "client_id",
    threshold: float = 85.0,
    method: str = "token_sort_ratio"
) -> List[Dict]:
    """
    Find potential duplicate records based on name similarity.
    
    Args:
        df: DataFrame containing client records
        name_column: Column name containing client names
        id_column: Column name containing client IDs
        threshold: Minimum similarity score to consider as duplicate (0-100)
        method: Matching method to use
        
    Returns:
        List of dictionaries containing duplicate pairs with:
        - id1, id2: Client IDs of potential duplicates
        - name1, name2: Client names
        - similarity: Similarity score
        - confidence: Confidence level (HIGH/MEDIUM/LOW)
    """
    logger.info(f"Finding duplicates with threshold {threshold}%")
    
    duplicates = []
    names = df[name_column].tolist()
    ids = df[id_column].tolist()
    
    # Compare each name with all others
    for i in range(len(names)):
        name1 = names[i]
        id1 = ids[i]
        
        # Skip if name is empty
        if not name1 or pd.isna(name1):
            continue
        
        # Compare with remaining names
        for j in range(i + 1, len(names)):
            name2 = names[j]
            id2 = ids[j]
            
            # Skip if name is empty
            if not name2 or pd.isna(name2):
                continue
            
            # Calculate similarity
            similarity = calculate_similarity(name1, name2, method)
            
            # Check if above threshold
            if similarity >= threshold:
                # Determine confidence level
                if similarity >= 95:
                    confidence = "HIGH"
                elif similarity >= 90:
                    confidence = "MEDIUM"
                else:
                    confidence = "LOW"
                
                duplicates.append({
                    "id1": id1,
                    "id2": id2,
                    "name1": name1,
                    "name2": name2,
                    "similarity": round(similarity, 2),
                    "confidence": confidence
                })
    
    logger.info(f"Found {len(duplicates)} potential duplicate pairs")
    
    # Log high confidence duplicates
    high_confidence = [d for d in duplicates if d["confidence"] == "HIGH"]
    if high_confidence:
        logger.warning(f"Found {len(high_confidence)} HIGH confidence duplicates")
        for dup in high_confidence[:5]:  # Show first 5
            logger.warning(
                f"  {dup['name1']} (ID: {dup['id1']}) <-> "
                f"{dup['name2']} (ID: {dup['id2']}) "
                f"[{dup['similarity']}%]"
            )
    
    return duplicates


def find_best_match(
    query: str,
    choices: List[str],
    threshold: float = 85.0,
    limit: int = 5
) -> List[Tuple[str, float]]:
    """
    Find best matching strings from a list of choices.
    
    Args:
        query: String to match
        choices: List of strings to match against
        threshold: Minimum similarity score
        limit: Maximum number of matches to return
        
    Returns:
        List of tuples (match, score) sorted by score descending
    """
    # Use rapidfuzz process.extract for efficient matching
    matches = process.extract(
        query,
        choices,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=threshold,
        limit=limit
    )
    
    return [(match[0], match[1]) for match in matches]


