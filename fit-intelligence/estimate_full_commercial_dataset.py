#!/usr/bin/env python3
"""
Estimate total commercial licenses in full dataset
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def estimate_commercial_licenses():
    """Estimate total commercial licenses across full dataset"""
    
    # From our analysis
    processed_total = 50000
    commercial_found = 7300
    commercial_rate = commercial_found / processed_total
    
    logger.info(f"COMMERCIAL LICENSE ESTIMATION")
    logger.info(f"="*50)
    logger.info(f"Processed sample: {processed_total:,} licenses")
    logger.info(f"Commercial in sample: {commercial_found:,} licenses")
    logger.info(f"Commercial rate: {commercial_rate:.1%}")
    
    # Full dataset estimates
    total_records_available = 869789  # From our earlier processing
    estimated_commercial = int(total_records_available * commercial_rate)
    
    logger.info(f"\nFULL DATASET PROJECTION:")
    logger.info(f"Total FIT records available: {total_records_available:,}")
    logger.info(f"Estimated commercial licenses: {estimated_commercial:,}")
    logger.info(f"Estimated domestic licenses: {total_records_available - estimated_commercial:,}")
    
    # Different commercial thresholds
    logger.info(f"\nCOMMERCIAL THRESHOLD SCENARIOS:")
    
    # Scenario 1: Current definition (non-domestic only)
    logger.info(f"Current (Non-Domestic only): ~{estimated_commercial:,} licenses")
    
    # Scenario 2: If 41k is the target, what would that represent?
    target_commercial = 41000
    required_rate = target_commercial / total_records_available
    logger.info(f"Target 41k commercial: {required_rate:.1%} of total dataset")
    
    # Scenario 3: Different capacity thresholds
    capacity_thresholds = [
        ("4kW+", "All above micro installations"),
        ("10kW+", "Small commercial and above"),
        ("50kW+", "Medium commercial and above"),
        ("100kW+", "Large installations only")
    ]
    
    for threshold, description in capacity_thresholds:
        # Based on our size distribution analysis
        if threshold == "4kW+":
            rate = 0.146  # Current non-domestic rate
        elif threshold == "10kW+":
            rate = 0.10   # Estimated
        elif threshold == "50kW+":
            rate = 0.08   # Estimated based on medium+ categories
        elif threshold == "100kW+":
            rate = 0.05   # Estimated based on large categories
        
        estimated = int(total_records_available * rate)
        logger.info(f"{threshold} ({description}): ~{estimated:,} licenses")
    
    logger.info(f"\n🎯 RECOMMENDATION:")
    if target_commercial <= estimated_commercial:
        logger.info(f"✓ 41k commercial licenses achievable with current definition")
        logger.info(f"✓ Represents ~{target_commercial/estimated_commercial:.1%} of available commercial licenses")
    else:
        logger.info(f"⚠️  41k target exceeds current commercial definition")
        logger.info(f"⚠️  May need to adjust commercial criteria or capacity thresholds")

if __name__ == "__main__":
    estimate_commercial_licenses()