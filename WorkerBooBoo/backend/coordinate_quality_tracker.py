#!/usr/bin/env python3
"""
Coordinate Quality Tracker
Tracks the quality and source of coordinates for workplace incidents
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Tuple
from dotenv import load_dotenv
from database import SessionLocal, WorkplaceIncident
from sqlalchemy import and_, func

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CoordinateQualityTracker:
    """Track and analyze coordinate quality for workplace incidents"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def analyze_coordinate_quality(self) -> Dict:
        """Analyze the quality of all coordinates in the database"""
        try:
            logger.info("🔍 Analyzing coordinate quality...")
            
            # Get all records with coordinates
            all_records = self.db.query(WorkplaceIncident).filter(
                WorkplaceIncident.latitude.isnot(None)
            ).all()
            
            total_records = len(all_records)
            logger.info(f"Found {total_records:,} records with coordinates")
            
            # Analyze coordinate precision
            very_precise = 0      # 6+ decimal places
            precise = 0           # 4-5 decimal places
            approximate = 0       # 2-3 decimal places
            rough = 0             # 0-1 decimal places
            
            # Analyze coordinate patterns
            likely_geocoded = 0   # Coordinates that look professionally geocoded
            likely_manual = 0     # Coordinates that look manually entered
            likely_fallback = 0   # Coordinates that look like fallbacks
            
            for record in all_records:
                lat, lng = record.latitude, record.longitude
                
                if lat and lng:
                    # Check precision (number of decimal places)
                    lat_str = str(lat).split('.')[-1] if '.' in str(lat) else '0'
                    lng_str = str(lng).split('.')[-1] if '.' in str(lng) else '0'
                    
                    max_precision = max(len(lat_str), len(lng_str))
                    
                    if max_precision >= 6:
                        very_precise += 1
                    elif max_precision >= 4:
                        precise += 1
                    elif max_precision >= 2:
                        approximate += 1
                    else:
                        rough += 1
                    
                    # Check if coordinates look professionally geocoded
                    # Professional geocoding typically produces coordinates with 5-6 decimal places
                    # and coordinates that don't follow obvious patterns
                    if max_precision >= 5 and not self._is_obvious_pattern(lat, lng):
                        likely_geocoded += 1
                    elif max_precision <= 2 or self._is_obvious_pattern(lat, lng):
                        likely_fallback += 1
                    else:
                        likely_manual += 1
            
            # Calculate percentages
            results = {
                'total_records': total_records,
                'precision_breakdown': {
                    'very_precise': very_precise,
                    'precise': precise,
                    'approximate': approximate,
                    'rough': rough
                },
                'source_breakdown': {
                    'likely_geocoded': likely_geocoded,
                    'likely_manual': likely_manual,
                    'likely_fallback': likely_fallback
                },
                'percentages': {
                    'very_precise_pct': (very_precise / total_records * 100) if total_records > 0 else 0,
                    'precise_pct': (precise / total_records * 100) if total_records > 0 else 0,
                    'approximate_pct': (approximate / total_records * 100) if total_records > 0 else 0,
                    'rough_pct': (rough / total_records * 100) if total_records > 0 else 0,
                    'geocoded_pct': (likely_geocoded / total_records * 100) if total_records > 0 else 0,
                    'fallback_pct': (likely_fallback / total_records * 100) if total_records > 0 else 0
                }
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing coordinate quality: {e}")
            return {}
    
    def _is_obvious_pattern(self, lat: float, lng: float) -> bool:
        """Check if coordinates follow obvious patterns (like state centers)"""
        if not lat or not lng:
            return False
        
        # Check if coordinates are very round numbers
        lat_round_0 = round(lat, 0)
        lng_round_0 = round(lng, 0)
        lat_round_1 = round(lat, 1)
        lng_round_1 = round(lng, 1)
        
        # State centers are often very round numbers
        if lat == lat_round_0 and lng == lng_round_0:
            return True
        
        # Check if coordinates are suspiciously similar to known state centers
        # This is a simplified check - you could expand this with actual state center coordinates
        suspicious_patterns = [
            (39.0, -105.0),  # Colorado
            (40.0, -100.0),  # Nebraska
            (35.0, -100.0),  # Oklahoma
            (30.0, -90.0),   # Louisiana
            (45.0, -100.0),  # North Dakota
        ]
        
        for pattern_lat, pattern_lng in suspicious_patterns:
            if abs(lat - pattern_lat) < 0.1 and abs(lng - pattern_lng) < 0.1:
                return True
        
        return False
    
    def get_records_needing_improvement(self, limit: int = 10) -> List[WorkplaceIncident]:
        """Get records that might benefit from better geocoding"""
        try:
            # Find records with low precision coordinates
            low_precision_records = self.db.query(WorkplaceIncident).filter(
                and_(
                    WorkplaceIncident.latitude.isnot(None),
                    WorkplaceIncident.longitude.isnot(None)
                )
            ).all()
            
            candidates = []
            for record in low_precision_records:
                lat, lng = record.latitude, record.longitude
                
                if lat and lng:
                    # Check if coordinates are low precision or follow obvious patterns
                    if self._is_obvious_pattern(lat, lng):
                        candidates.append(record)
                    
                    # Also check for very low precision
                    lat_str = str(lat).split('.')[-1] if '.' in str(lat) else '0'
                    lng_str = str(lng).split('.')[-1] if '.' in str(lng) else '0'
                    
                    if len(lat_str) <= 2 or len(lng_str) <= 2:
                        candidates.append(record)
            
            # Remove duplicates and limit results
            unique_candidates = list({record.id: record for record in candidates}.values())
            return unique_candidates[:limit]
            
        except Exception as e:
            logger.error(f"Error getting records needing improvement: {e}")
            return []
    
    def generate_quality_report(self) -> str:
        """Generate a comprehensive quality report"""
        try:
            analysis = self.analyze_coordinate_quality()
            
            if not analysis:
                return "❌ Failed to analyze coordinate quality"
            
            report = []
            report.append("=" * 60)
            report.append("📊 COORDINATE QUALITY REPORT")
            report.append("=" * 60)
            report.append(f"📋 Total Records: {analysis['total_records']:,}")
            report.append("")
            
            # Precision breakdown
            report.append("🎯 PRECISION BREAKDOWN:")
            report.append(f"   Very Precise (6+ decimals): {analysis['precision_breakdown']['very_precise']:,} ({analysis['percentages']['very_precise_pct']:.1f}%)")
            report.append(f"   Precise (4-5 decimals): {analysis['precision_breakdown']['precise']:,} ({analysis['percentages']['precise_pct']:.1f}%)")
            report.append(f"   Approximate (2-3 decimals): {analysis['precision_breakdown']['approximate']:,} ({analysis['percentages']['approximate_pct']:.1f}%)")
            report.append(f"   Rough (0-1 decimals): {analysis['precision_breakdown']['rough']:,} ({analysis['percentages']['rough_pct']:.1f}%)")
            report.append("")
            
            # Source breakdown
            report.append("🔍 SOURCE BREAKDOWN:")
            report.append(f"   Likely Professional Geocoding: {analysis['source_breakdown']['likely_geocoded']:,} ({analysis['percentages']['geocoded_pct']:.1f}%)")
            report.append(f"   Likely Manual Entry: {analysis['source_breakdown']['likely_manual']:,}")
            report.append(f"   Likely Fallback Coordinates: {analysis['source_breakdown']['likely_fallback']:,} ({analysis['percentages']['fallback_pct']:.1f}%)")
            report.append("")
            
            # Quality assessment
            if analysis['percentages']['geocoded_pct'] >= 90:
                report.append("🏆 QUALITY ASSESSMENT: EXCELLENT")
                report.append("   Your coordinates are of professional quality!")
            elif analysis['percentages']['geocoded_pct'] >= 70:
                report.append("✅ QUALITY ASSESSMENT: GOOD")
                report.append("   Most coordinates are high quality")
            elif analysis['percentages']['geocoded_pct'] >= 50:
                report.append("⚠️  QUALITY ASSESSMENT: FAIR")
                report.append("   Some coordinates could be improved")
            else:
                report.append("❌ QUALITY ASSESSMENT: NEEDS IMPROVEMENT")
                report.append("   Many coordinates appear to be fallbacks")
            
            report.append("=" * 60)
            
            return "\n".join(report)
            
        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            return f"❌ Error generating report: {e}"
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()

def main():
    """Main function to run coordinate quality analysis"""
    tracker = CoordinateQualityTracker()
    
    try:
        # Generate and display quality report
        report = tracker.generate_quality_report()
        print(report)
        
        # Show records that might need improvement
        print("\n🔍 RECORDS THAT MIGHT NEED IMPROVEMENT:")
        print("=" * 60)
        
        improvement_candidates = tracker.get_records_needing_improvement(limit=5)
        
        if improvement_candidates:
            for i, record in enumerate(improvement_candidates, 1):
                lat, lng = record.latitude, record.longitude
                print(f"{i}. {record.company_name[:40]:<40} | {record.city}, {record.state} | ({lat:.6f}, {lng:.6f})")
        else:
            print("✅ No records identified as needing improvement!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        tracker.close()

if __name__ == "__main__":
    main()
