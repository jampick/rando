"""
Icon Category Mapping Logic

This module provides functions to map detailed OIICS (Occupational Injury and Illness Classification System)
data into simplified icon categories for visual storytelling in the UI.
"""

import re
from typing import Optional

class IconCategoryMapper:
    """Maps detailed OIICS data to simplified icon categories"""
    
    def __init__(self):
        # Injury category keywords
        self.injury_keywords = {
            'fracture': [
                'fracture', 'broken', 'break', 'crack', 'shatter', 'crush', 'compression',
                'dislocation', 'displaced', 'bone', 'skeletal', 'lower leg', 'leg', 'arm',
                'hand', 'foot', 'ankle', 'wrist', 'elbow', 'knee', 'shoulder', 'hip'
            ],
            'amputation': [
                'amputation', 'amputated', 'severed', 'cut off', 'removed', 'detached',
                'lost', 'missing', 'partial amputation', 'finger', 'toe', 'digit'
            ],
            'burn': [
                'burn', 'thermal', 'heat', 'fire', 'flame', 'scald', 'chemical burn',
                'electrical burn', 'radiation burn', 'frostbite', 'corrosion'
            ],
            'electrocution': [
                'electrocution', 'electric shock', 'electrical', 'shock', 'current',
                'voltage', 'electrical injury', 'electrical burn'
            ],
            'head_injury': [
                'concussion', 'contusion', 'intracranial', 'head injury', 'brain injury',
                'skull fracture', 'traumatic brain injury', 'tbi', 'head trauma'
            ],
            'cut': [
                'cut', 'laceration', 'puncture', 'stab', 'slice', 'gash', 'tear',
                'incision', 'wound', 'bleeding', 'hemorrhage'
            ],
            'sprain_strain': [
                'sprain', 'strain', 'tear', 'pull', 'twist', 'overextension',
                'muscle injury', 'ligament', 'tendon', 'soft tissue'
            ],
            'asphyxiation': [
                'asphyxiation', 'suffocation', 'choking', 'strangulation', 'drowning',
                'oxygen deprivation', 'respiratory', 'breathing'
            ]
        }
        
        # Event category keywords
        self.event_keywords = {
            'fall': [
                'fall', 'fell', 'falling', 'slipped', 'tripped', 'stumbled',
                'plunge', 'drop', 'descend', 'elevation'
            ],
            'struck_by': [
                'struck by', 'hit by', 'impacted by', 'contact with', 'collision with',
                'bumped by', 'knocked by', 'falling object', 'falling equipment'
            ],
            'struck_against': [
                'struck against', 'hit against', 'contact with', 'bumped into',
                'collision with', 'impact with'
            ],
            'caught_in': [
                'caught in', 'caught between', 'entangled', 'trapped', 'pinched',
                'crushed between', 'squeezed'
            ],
            'exposure': [
                'exposure', 'exposed to', 'contact with', 'inhalation', 'ingestion',
                'absorption', 'environmental', 'chemical exposure'
            ],
            'transportation': [
                'transportation', 'vehicle', 'motor vehicle', 'traffic', 'roadway',
                'highway', 'collision', 'accident', 'crash'
            ],
            'violence_animal': [
                'violence', 'assault', 'attack', 'bite', 'kick', 'punch', 'animal',
                'human', 'aggressive', 'hostile'
            ]
        }
        
        # Source category keywords
        self.source_keywords = {
            'machinery': [
                'machinery', 'machine', 'equipment', 'industrial', 'manufacturing',
                'production', 'assembly', 'conveyor', 'press', 'mill'
            ],
            'tools': [
                'tool', 'hand tool', 'power tool', 'saw', 'drill', 'hammer',
                'wrench', 'screwdriver', 'knife', 'blade'
            ],
            'vehicles': [
                'vehicle', 'truck', 'car', 'forklift', 'crane', 'bulldozer',
                'tractor', 'motor vehicle', 'automobile'
            ],
            'ladders_scaffolds': [
                'ladder', 'scaffold', 'scaffolding', 'manlift', 'elevation',
                'platform', 'lift', 'hoist'
            ],
            'structures_surfaces': [
                'floor', 'surface', 'structure', 'wall', 'ceiling', 'roof',
                'ground', 'pavement', 'concrete', 'asphalt', 'ramp', 'dock', 'plate'
            ],
            'chemicals': [
                'chemical', 'acid', 'base', 'solvent', 'paint', 'adhesive',
                'cleaning', 'detergent', 'toxic', 'hazardous'
            ],
            'fire_heat': [
                'fire', 'heat', 'flame', 'hot', 'thermal', 'furnace', 'oven',
                'boiler', 'steam', 'molten', 'welding', 'cutting', 'blow torch'
            ],
            'electricity': [
                'electric', 'electrical', 'power', 'voltage', 'current',
                'wiring', 'outlet', 'switch', 'circuit'
            ],
            'environmental': [
                'weather', 'climate', 'temperature', 'wind', 'rain', 'snow',
                'ice', 'natural', 'environmental', 'atmospheric'
            ],
            'animals_people': [
                'animal', 'person', 'human', 'coworker', 'patient', 'customer',
                'client', 'public', 'crowd'
            ],
            'materials_objects': [
                'material', 'object', 'pallet', 'pipe', 'box', 'container',
                'package', 'crate', 'barrel', 'drum'
            ]
        }
    
    def map_injury_category(self, body_part: Optional[str], incident_type: Optional[str] = None) -> str:
        """Map injury details to icon injury category"""
        if not body_part:
            return "other"
        
        # Convert to lowercase for matching
        text = body_part.lower()
        
        # Check each category
        for category, keywords in self.injury_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        # Special case for incident_type
        if incident_type and 'amputation' in incident_type.lower():
            return "amputation"
        
        return "other"
    
    def map_event_category(self, event_type: Optional[str]) -> str:
        """Map event details to icon event category"""
        if not event_type:
            return "other"
        
        # Convert to lowercase for matching
        text = event_type.lower()
        
        # Check each category
        for category, keywords in self.event_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "other"
    
    def map_source_category(self, source: Optional[str]) -> str:
        """Map source details to icon source category"""
        if not source:
            return "other"
        
        # Convert to lowercase for matching
        text = source.lower()
        
        # Check each category
        for category, keywords in self.source_keywords.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return "other"
    
    def map_severity_category(self, hospitalized: Optional[bool], amputation: Optional[bool], 
                             incident_type: Optional[str] = None) -> str:
        """Map severity indicators to icon severity category"""
        # Check amputation first (highest severity)
        if amputation:
            return "amputation"
        
        # Check for fatality in incident_type
        if incident_type and 'fatality' in incident_type.lower():
            return "fatality"
        
        # Check hospitalization
        if hospitalized:
            return "hospitalized"
        
        # Default to minor
        return "minor"
    
    def map_all_categories(self, body_part: Optional[str] = None, event_type: Optional[str] = None,
                          source: Optional[str] = None, hospitalized: Optional[bool] = None,
                          amputation: Optional[bool] = None, incident_type: Optional[str] = None) -> dict:
        """Map all categories at once"""
        return {
            'icon_injury': self.map_injury_category(body_part, incident_type),
            'icon_event': self.map_event_category(event_type),
            'icon_source': self.map_source_category(source),
            'icon_severity': self.map_severity_category(hospitalized, amputation, incident_type)
        }

# Global instance for easy access
icon_mapper = IconCategoryMapper()
