#!/usr/bin/env python3
"""
Populate Sample OIICS Data
This script populates the OIICS fields with sample data based on incident types
for demonstration purposes when source data matching isn't available.
"""

import sys
import logging
from datetime import datetime
from typing import Dict, List
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, WorkplaceIncident

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SampleOIICSPopulator:
    """Populate OIICS fields with sample data based on incident types"""
    
    def __init__(self):
        # Sample OIICS data mappings based on incident types
        self.oiics_mappings = {
            'Amputations': {
                'body_part': 'Hand/Finger',
                'event_type': 'Caught in/between objects',
                'source': 'Machinery',
                'secondary_source': 'Moving parts',
                'hospitalized': True,
                'amputation': True
            },
            'Fractures': {
                'body_part': 'Arm/Leg',
                'event_type': 'Fall to lower level',
                'source': 'Floor/surface',
                'secondary_source': 'Height',
                'hospitalized': True,
                'amputation': False
            },
            'Burns': {
                'body_part': 'Hand/Arm',
                'event_type': 'Contact with hot object',
                'source': 'Hot equipment',
                'secondary_source': 'Temperature',
                'hospitalized': False,
                'amputation': False
            },
            'Cerebral and other intracranial hemorrhages': {
                'body_part': 'Head',
                'event_type': 'Struck by object',
                'source': 'Falling object',
                'secondary_source': 'Gravity',
                'hospitalized': True,
                'amputation': False
            },
            'Puncture wounds, except gunshot wounds': {
                'body_part': 'Leg',
                'event_type': 'Struck by object',
                'source': 'Sharp object',
                'secondary_source': 'Tools',
                'hospitalized': False,
                'amputation': False
            },
            'Soreness, pain, hurt-nonspecified injury': {
                'body_part': 'Back',
                'event_type': 'Overexertion',
                'source': 'Manual handling',
                'secondary_source': 'Weight',
                'hospitalized': False,
                'amputation': False
            }
        }
        
        # Default OIICS data for unknown incident types
        self.default_oiics = {
            'body_part': 'Multiple parts',
            'event_type': 'Other event',
            'source': 'Other source',
            'secondary_source': 'Environmental factors',
            'hospitalized': False,
            'amputation': False
        }
    
    def get_oiics_data(self, incident_type: str) -> Dict:
        """Get OIICS data for a given incident type"""
        # Try to find exact match
        if incident_type in self.oiics_mappings:
            return self.oiics_mappings[incident_type].copy()
        
        # Try partial matches
        incident_lower = incident_type.lower()
        for key, value in self.oiics_mappings.items():
            if any(word in incident_lower for word in key.lower().split()):
                return value.copy()
        
        # Return default if no match found
        return self.default_oiics.copy()
    
    def populate_sample_oiics(self) -> Dict:
        """Populate all incidents with sample OIICS data"""
        logger.info("🚀 Starting sample OIICS data population...")
        
        db = SessionLocal()
        results = {
            'total_incidents': 0,
            'updated_incidents': 0,
            'incident_types_processed': set(),
            'errors': []
        }
        
        try:
            # Get all incidents
            incidents = db.query(WorkplaceIncident).all()
            results['total_incidents'] = len(incidents)
            logger.info(f"Found {len(incidents)} incidents to process")
            
            for i, incident in enumerate(incidents):
                if i % 10000 == 0:
                    logger.info(f"Processing incident {i:,} of {len(incidents):,}")
                
                try:
                    # Get OIICS data for this incident type
                    oiics_data = self.get_oiics_data(incident.incident_type)
                    
                    # Update the incident
                    incident.body_part = oiics_data['body_part']
                    incident.event_type = oiics_data['event_type']
                    incident.source = oiics_data['source']
                    incident.secondary_source = oiics_data['secondary_source']
                    incident.hospitalized = oiics_data['hospitalized']
                    incident.amputation = oiics_data['amputation']
                    
                    # Add sample inspection and jurisdiction data
                    incident.inspection_id = f"INS-{incident.osha_id}"
                    incident.jurisdiction = "Federal"
                    
                    incident.updated_at = datetime.now()
                    
                    results['updated_incidents'] += 1
                    results['incident_types_processed'].add(incident.incident_type)
                    
                except Exception as e:
                    error_msg = f"Error updating incident {incident.id}: {e}"
                    logger.warning(error_msg)
                    results['errors'].append(error_msg)
            
            # Commit all changes
            db.commit()
            logger.info(f"✅ Successfully updated {results['updated_incidents']} incidents with sample OIICS data")
            
        except Exception as e:
            logger.error(f"Error during population: {e}")
            db.rollback()
            raise
        finally:
            db.close()
        
        return results
    
    def validate_population(self) -> Dict:
        """Validate the populated OIICS data"""
        logger.info("Validating populated OIICS data...")
        
        db = SessionLocal()
        validation_results = {
            'total_incidents': 0,
            'incidents_with_oiics': 0,
            'oiics_field_counts': {},
            'sample_incidents': []
        }
        
        try:
            # Get total incidents
            total_incidents = db.query(WorkplaceIncident).count()
            validation_results['total_incidents'] = total_incidents
            
            # Count incidents with OIICS data
            incidents_with_oiics = db.query(WorkplaceIncident).filter(
                (WorkplaceIncident.body_part.isnot(None)) |
                (WorkplaceIncident.event_type.isnot(None)) |
                (WorkplaceIncident.source.isnot(None)) |
                (WorkplaceIncident.hospitalized.isnot(None)) |
                (WorkplaceIncident.amputation.isnot(None))
            ).count()
            validation_results['incidents_with_oiics'] = incidents_with_oiics
            
            # Count each OIICS field
            oiics_fields = ['body_part', 'event_type', 'source', 'secondary_source', 
                           'hospitalized', 'amputation', 'inspection_id', 'jurisdiction']
            
            for field in oiics_fields:
                count = db.query(WorkplaceIncident).filter(
                    getattr(WorkplaceIncident, field).isnot(None)
                ).count()
                validation_results['oiics_field_counts'][field] = count
            
            # Get sample incidents with OIICS data
            sample_incidents = db.query(WorkplaceIncident).filter(
                (WorkplaceIncident.body_part.isnot(None)) |
                (WorkplaceIncident.event_type.isnot(None)) |
                (WorkplaceIncident.source.isnot(None))
            ).limit(5).all()
            
            for incident in sample_incidents:
                sample_data = {
                    'id': incident.id,
                    'osha_id': incident.osha_id,
                    'company_name': incident.company_name,
                    'incident_type': incident.incident_type,
                    'oiics_fields': {
                        'body_part': incident.body_part,
                        'event_type': incident.event_type,
                        'source': incident.source,
                        'secondary_source': incident.secondary_source,
                        'hospitalized': incident.hospitalized,
                        'amputation': incident.amputation,
                        'inspection_id': incident.inspection_id,
                        'jurisdiction': incident.jurisdiction
                    }
                }
                validation_results['sample_incidents'].append(sample_data)
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            raise
        finally:
            db.close()
        
        return validation_results

def main():
    """Main function"""
    logger.info("🎯 Starting Sample OIICS Data Population")
    
    try:
        # Initialize populator
        populator = SampleOIICSPopulator()
        
        # Populate sample OIICS data
        results = populator.populate_sample_oiics()
        
        # Validate the results
        validation_results = populator.validate_population()
        
        # Display results
        logger.info("\n" + "="*60)
        logger.info("📊 POPULATION RESULTS SUMMARY")
        logger.info("="*60)
        
        logger.info(f"Total incidents: {results['total_incidents']}")
        logger.info(f"Updated incidents: {results['updated_incidents']}")
        logger.info(f"Incident types processed: {len(results['incident_types_processed'])}")
        
        if results['incident_types_processed']:
            logger.info("\nIncident types processed:")
            for incident_type in sorted(results['incident_types_processed']):
                logger.info(f"  - {incident_type}")
        
        if validation_results:
            logger.info("\nValidation Results:")
            validation = validation_results
            logger.info(f"  Total incidents: {validation['total_incidents']}")
            logger.info(f"  Incidents with OIICS data: {validation['incidents_with_oiics']}")
            logger.info(f"  OIICS coverage: {(validation['incidents_with_oiics']/validation['total_incidents']*100):.1f}%")
            
            logger.info("\nOIICS field counts:")
            for field, count in validation['oiics_field_counts'].items():
                logger.info(f"  {field}: {count}")
            
            if validation['sample_incidents']:
                logger.info("\nSample incidents with OIICS data:")
                for i, incident in enumerate(validation['sample_incidents'][:3], 1):
                    logger.info(f"  {i}. {incident['company_name']} - {incident['incident_type']}")
                    oiics_fields = incident['oiics_fields']
                    if oiics_fields['body_part']:
                        logger.info(f"     Body Part: {oiics_fields['body_part']}")
                    if oiics_fields['source']:
                        logger.info(f"     Source: {oiics_fields['source']}")
        
        if results['errors']:
            logger.warning(f"\n⚠️  {len(results['errors'])} errors encountered:")
            for error in results['errors']:
                logger.warning(f"  - {error}")
        
        logger.info("\n🎉 Sample OIICS data population completed!")
        logger.info("Note: This is sample data for demonstration purposes.")
        logger.info("Real OIICS data should be imported from OSHA source files.")
        return 0
        
    except Exception as e:
        logger.error(f"❌ Population failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
