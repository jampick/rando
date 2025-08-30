# OIICS Fields Guide

## Overview

This guide explains the new OIICS (Occupational Injury and Illness Classification System) fields that have been added to the WorkerBooBoo incident tracking system. These fields provide standardized classification of workplace injuries and illnesses according to OSHA standards.

## What is OIICS?

OIICS is a standardized system developed by the Bureau of Labor Statistics (BLS) and OSHA to classify workplace injuries and illnesses. It provides consistent terminology and coding for:

- **Nature of Injury**: What type of injury occurred (e.g., fracture, burn, amputation)
- **Part of Body**: Which part of the body was affected
- **Event/Exposure**: How the injury occurred (e.g., fall, struck by object)
- **Source**: What object or substance caused the injury
- **Secondary Source**: Additional contributing factors

## New Fields Added

### 1. Body Part (`body_part`)
- **Description**: The specific part of the body affected by the injury
- **Source**: Maps from OSHA SIR data "Part of Body Title"
- **Examples**: Head, Neck, Back, Shoulder, Arm, Hand, Leg, Foot, Multiple parts
- **Use Case**: Identify injury patterns by body part across incidents

### 2. Event Type (`event_type`)
- **Description**: The type of event that caused the injury
- **Source**: Maps from OSHA SIR data "EventTitle"
- **Examples**: Fall, Struck by object, Caught in/between, Contact with object, Overexertion
- **Use Case**: Analyze incident causation patterns and prevention strategies

### 3. Source (`source`)
- **Description**: The primary object, substance, or equipment that caused the injury
- **Source**: Maps from OSHA SIR data "SourceTitle"
- **Examples**: Machinery, Tools, Chemicals, Vehicles, Building/structure, Floor/surface
- **Use Case**: Identify hazardous equipment or substances for targeted safety improvements

### 4. Secondary Source (`secondary_source`)
- **Description**: Additional contributing factors or secondary sources
- **Source**: Maps from OSHA SIR data "Secondary Source Title"
- **Examples**: Secondary equipment, environmental factors, contributing substances
- **Use Case**: Understand complex incident scenarios with multiple contributing factors

### 5. Hospitalized (`hospitalized`)
- **Description**: Whether the injured worker required hospitalization
- **Source**: Maps from OSHA SIR data "Hospitalized" field
- **Values**: Boolean (true/false)
- **Use Case**: Track severity of injuries and medical resource utilization

### 6. Amputation (`amputation`)
- **Description**: Whether the incident resulted in an amputation
- **Source**: Maps from OSHA SIR data "Amputation" field
- **Values**: Boolean (true/false)
- **Use Case**: Identify severe incidents requiring special attention and reporting

### 7. Inspection ID (`inspection_id`)
- **Description**: OSHA inspection identifier for the incident
- **Source**: Maps from OSHA data inspection fields
- **Use Case**: Link incidents to OSHA inspection reports and enforcement actions

### 8. Jurisdiction (`jurisdiction`)
- **Description**: Whether federal or state OSHA has jurisdiction
- **Source**: Maps from OSHA data "FederalState" field
- **Values**: "Federal", "State", or specific state name
- **Use Case**: Understand regulatory oversight and reporting requirements

## Data Sources

These fields are populated from:

1. **OSHA SIR (Serious Injury Report) Data**: Primary source for injury classification
2. **OSHA Fatality Data**: Source of fatality event and source information
3. **OSHA Inspection Data**: Inspection IDs and jurisdiction information

## Benefits

### For Safety Professionals
- **Standardized Classification**: Consistent injury coding across all incidents
- **Pattern Recognition**: Identify common injury types, body parts, and sources
- **Prevention Targeting**: Focus safety improvements on high-risk areas
- **Regulatory Compliance**: Meet OSHA reporting and classification requirements

### For Data Analysis
- **Trend Analysis**: Track injury patterns over time
- **Risk Assessment**: Identify high-risk operations and equipment
- **Benchmarking**: Compare injury rates by classification across industries
- **ROI Measurement**: Measure effectiveness of safety interventions

### For Incident Investigation
- **Root Cause Analysis**: Understand contributing factors and sources
- **Similar Incident Search**: Find comparable incidents for learning
- **Prevention Strategy**: Develop targeted prevention measures

## Implementation

### Database Migration
Run the migration script to add these fields to existing databases:

**Windows:**
```batch
migrate_add_oiics_fields.bat
```

**Unix/Mac:**
```bash
./migrate_add_oiics_fields.sh
```

### Frontend Display
The new fields are automatically displayed in incident cards when data is available:

- **OIICS Classification Section**: Orange-themed section showing injury details
- **Investigation Status Section**: Additional inspection and jurisdiction information
- **Conditional Display**: Fields only show when data is available

### Data Import
When importing new OSHA data, these fields will be automatically populated based on the source data format (SIR vs. fatality data).

## Example Usage

### Incident Card Display
```
Injury Classification (OIICS)
├── Body Part: Hand
├── Event Type: Struck by object
├── Source: Machinery
├── Secondary Source: Metal part
├── Hospitalized: Yes
└── Amputation: No

Investigation Status
├── Status: Open
├── Inspection ID: 1234567
├── Jurisdiction: Federal
├── Citations: No
└── Penalty: $0.00
```

### Data Analysis Queries
```sql
-- Most common injury types by body part
SELECT body_part, COUNT(*) as incident_count
FROM workplace_incidents
WHERE body_part IS NOT NULL
GROUP BY body_part
ORDER BY incident_count DESC;

-- Hospitalization rate by source
SELECT source, 
       COUNT(*) as total_incidents,
       SUM(CASE WHEN hospitalized = 1 THEN 1 ELSE 0 END) as hospitalized_count,
       ROUND(CAST(SUM(CASE WHEN hospitalized = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 2) as hospitalization_rate
FROM workplace_incidents
WHERE source IS NOT NULL
GROUP BY source
HAVING total_incidents >= 5
ORDER BY hospitalization_rate DESC;
```

## Best Practices

### Data Quality
1. **Validate Field Values**: Ensure OIICS classifications follow standard terminology
2. **Complete Data**: Fill all available fields for comprehensive incident analysis
3. **Consistent Coding**: Use standardized terms across all incidents

### Analysis
1. **Regular Reviews**: Analyze injury patterns monthly/quarterly
2. **Trend Monitoring**: Track changes in injury types and sources over time
3. **Action Planning**: Use insights to prioritize safety improvements

### Reporting
1. **OSHA Compliance**: Ensure all required fields are completed for regulatory reporting
2. **Internal Communication**: Share injury pattern insights with safety teams
3. **Management Updates**: Provide regular reports on injury trends and prevention efforts

## Future Enhancements

Potential future additions to the OIICS system:

- **Activity Codes**: What the worker was doing when injured
- **Location Codes**: Specific location within the workplace
- **Industry-Specific Classifications**: Specialized codes for construction, manufacturing, etc.
- **Severity Indicators**: More detailed injury severity classifications
- **Recovery Time**: Days away from work or restricted duty

## Support

For questions about OIICS fields or implementation:

1. **Documentation**: Check this guide and related technical documentation
2. **Data Issues**: Review OSHA data processing scripts for field mapping
3. **Display Issues**: Check frontend incident card components
4. **Migration Problems**: Review migration script logs and database schema

---

*This guide covers the implementation of OIICS fields in WorkerBooBoo v2.0. For updates and additional features, check the project documentation.*
