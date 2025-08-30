#!/usr/bin/env python3
"""
Database Migration Script: Add OIICS Fields
Adds new OIICS (Occupational Injury and Illness Classification System) fields to existing databases
"""

import sqlite3
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_database(db_path: str = "workplace_safety.db"):
    """Add OIICS fields to existing database"""
    
    if not Path(db_path).exists():
        logger.error(f"Database file not found: {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        logger.info("Starting database migration to add OIICS fields...")
        
        # Check if fields already exist
        cursor.execute("PRAGMA table_info(workplace_incidents)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # Define new OIICS fields to add
        new_fields = [
            ('body_part', 'TEXT'),
            ('event_type', 'TEXT'),
            ('source', 'TEXT'),
            ('secondary_source', 'TEXT'),
            ('hospitalized', 'BOOLEAN'),
            ('amputation', 'BOOLEAN'),
            ('inspection_id', 'TEXT'),
            ('jurisdiction', 'TEXT')
        ]
        
        # Add new fields that don't exist
        fields_added = 0
        for field_name, field_type in new_fields:
            if field_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE workplace_incidents ADD COLUMN {field_name} {field_type}")
                    logger.info(f"✓ Added field: {field_name} ({field_type})")
                    fields_added += 1
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e):
                        logger.info(f"Field {field_name} already exists, skipping...")
                    else:
                        logger.warning(f"Could not add field {field_name}: {e}")
            else:
                logger.info(f"Field {field_name} already exists, skipping...")
        
        # Commit changes
        conn.commit()
        
        if fields_added > 0:
            logger.info(f"✅ Migration completed successfully! Added {fields_added} new fields.")
        else:
            logger.info("✅ Migration completed - all fields already exist.")
        
        # Verify the new structure
        cursor.execute("PRAGMA table_info(workplace_incidents)")
        final_columns = [column[1] for column in cursor.fetchall()]
        logger.info(f"Final table structure has {len(final_columns)} columns:")
        for column in final_columns:
            logger.info(f"  - {column}")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False
        
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main migration function"""
    logger.info("🚀 Starting OIICS fields migration...")
    
    # Try to migrate the database
    success = migrate_database()
    
    if success:
        logger.info("🎉 Migration completed successfully!")
        logger.info("")
        logger.info("New OIICS fields added:")
        logger.info("  - body_part: Body part affected by injury")
        logger.info("  - event_type: Type of event that caused injury")
        logger.info("  - source: Primary source of injury")
        logger.info("  - secondary_source: Secondary source of injury")
        logger.info("  - hospitalized: Whether worker was hospitalized")
        logger.info("  - amputation: Whether amputation occurred")
        logger.info("  - inspection_id: OSHA inspection identifier")
        logger.info("  - jurisdiction: Federal or state OSHA jurisdiction")
        logger.info("")
        logger.info("These fields will now be available in incident cards and data processing.")
    else:
        logger.error("❌ Migration failed!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
