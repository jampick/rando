#!/usr/bin/env python3
"""
Migration Script: Add Icon Category Fields
This script adds the new icon category fields to the existing database
"""

import os
import sys
import logging
from datetime import datetime
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, WorkplaceIncident, Base, engine
from icon_categories import icon_mapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def add_icon_columns():
    """Add icon category columns to the database"""
    logger.info("🔧 Adding icon category columns to database...")
    
    try:
        # Create a connection to execute raw SQL
        with engine.connect() as connection:
            # Check if columns already exist
            result = connection.execute(text("""
                PRAGMA table_info(workplace_incidents)
            """))
            existing_columns = [row[1] for row in result.fetchall()]
            
            # Add columns if they don't exist
            columns_to_add = [
                'icon_injury',
                'icon_event', 
                'icon_source',
                'icon_severity'
            ]
            
            for column in columns_to_add:
                if column not in existing_columns:
                    logger.info(f"Adding column: {column}")
                    connection.execute(text(f"""
                        ALTER TABLE workplace_incidents 
                        ADD COLUMN {column} TEXT
                    """))
                    connection.commit()
                    logger.info(f"✓ Added column: {column}")
                else:
                    logger.info(f"Column already exists: {column}")
            
            logger.info("✅ All icon category columns added successfully")
            
    except Exception as e:
        logger.error(f"❌ Error adding columns: {e}")
        raise

def populate_icon_fields():
    """Populate icon category fields for existing records"""
    logger.info("🔄 Populating icon category fields...")
    
    db = SessionLocal()
    try:
        # Get all incidents that don't have icon fields populated
        incidents = db.query(WorkplaceIncident).filter(
            (WorkplaceIncident.icon_injury.is_(None)) |
            (WorkplaceIncident.icon_event.is_(None)) |
            (WorkplaceIncident.icon_source.is_(None)) |
            (WorkplaceIncident.icon_severity.is_(None))
        ).all()
        
        logger.info(f"Found {len(incidents)} incidents to update")
        
        updated_count = 0
        for incident in incidents:
            try:
                # Map icon categories
                icon_categories = icon_mapper.map_all_categories(
                    body_part=incident.body_part,
                    event_type=incident.event_type,
                    source=incident.source,
                    hospitalized=incident.hospitalized,
                    amputation=incident.amputation,
                    incident_type=incident.incident_type
                )
                
                # Update the incident
                incident.icon_injury = icon_categories['icon_injury']
                incident.icon_event = icon_categories['icon_event']
                incident.icon_source = icon_categories['icon_source']
                incident.icon_severity = icon_categories['icon_severity']
                incident.updated_at = datetime.now()
                
                updated_count += 1
                
                if updated_count % 1000 == 0:
                    logger.info(f"Updated {updated_count} incidents...")
                    
            except Exception as e:
                logger.warning(f"Error updating incident {incident.id}: {e}")
                continue
        
        # Commit all changes
        db.commit()
        logger.info(f"✅ Successfully updated {updated_count} incidents")
        
    except Exception as e:
        logger.error(f"❌ Error populating icon fields: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def validate_migration():
    """Validate the migration results"""
    logger.info("🔍 Validating migration results...")
    
    db = SessionLocal()
    try:
        # Count total incidents
        total_incidents = db.query(WorkplaceIncident).count()
        
        # Count incidents with icon fields
        incidents_with_icons = db.query(WorkplaceIncident).filter(
            (WorkplaceIncident.icon_injury.isnot(None)) &
            (WorkplaceIncident.icon_event.isnot(None)) &
            (WorkplaceIncident.icon_source.isnot(None)) &
            (WorkplaceIncident.icon_severity.isnot(None))
        ).count()
        
        # Get icon category distributions
        icon_injury_counts = db.query(WorkplaceIncident.icon_injury, 
                                     func.count(WorkplaceIncident.id)).group_by(
            WorkplaceIncident.icon_injury).all()
        
        icon_event_counts = db.query(WorkplaceIncident.icon_event, 
                                    func.count(WorkplaceIncident.id)).group_by(
            WorkplaceIncident.icon_event).all()
        
        icon_source_counts = db.query(WorkplaceIncident.icon_source, 
                                     func.count(WorkplaceIncident.id)).group_by(
            WorkplaceIncident.icon_source).all()
        
        icon_severity_counts = db.query(WorkplaceIncident.icon_severity, 
                                       func.count(WorkplaceIncident.id)).group_by(
            WorkplaceIncident.icon_severity).all()
        
        # Print results
        logger.info(f"📊 Migration Validation Results:")
        logger.info(f"  Total incidents: {total_incidents}")
        logger.info(f"  Incidents with icon fields: {incidents_with_icons}")
        logger.info(f"  Icon coverage: {(incidents_with_icons/total_incidents)*100:.1f}%")
        
        logger.info(f"  Icon Injury Distribution:")
        for category, count in icon_injury_counts:
            logger.info(f"    {category}: {count}")
        
        logger.info(f"  Icon Event Distribution:")
        for category, count in icon_event_counts:
            logger.info(f"    {category}: {count}")
        
        logger.info(f"  Icon Source Distribution:")
        for category, count in icon_source_counts:
            logger.info(f"    {category}: {count}")
        
        logger.info(f"  Icon Severity Distribution:")
        for category, count in icon_severity_counts:
            logger.info(f"    {category}: {count}")
        
        # Get sample incidents
        sample_incidents = db.query(WorkplaceIncident).filter(
            WorkplaceIncident.icon_injury.isnot(None)
        ).limit(3).all()
        
        logger.info(f"  Sample incidents with icon fields:")
        for incident in sample_incidents:
            logger.info(f"    ID {incident.id}: {incident.company_name}")
            logger.info(f"      Injury: {incident.icon_injury}, Event: {incident.icon_event}")
            logger.info(f"      Source: {incident.icon_source}, Severity: {incident.icon_severity}")
        
    except Exception as e:
        logger.error(f"❌ Error during validation: {e}")
        raise
    finally:
        db.close()

def main():
    """Main migration function"""
    logger.info("🚀 Starting Icon Category Migration")
    
    try:
        # Step 1: Add columns
        add_icon_columns()
        
        # Step 2: Populate fields
        populate_icon_fields()
        
        # Step 3: Validate
        validate_migration()
        
        logger.info("🎉 Icon category migration completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    main()
