# 🏭 OSHA Data Processing Guide

This guide shows you how to process different types of OSHA data using our unified data processor.

## 📊 **Supported Data Types**

- **SIR (Serious Injury Reports)** - Non-fatal workplace injuries
- **Fatality Data** - Workplace fatalities
- **Inspection Data** - OSHA inspection results
- **Auto-detection** - Automatically determines data type

## 🚀 **Quick Start**

### **1. Download OSHA Data**

Get your data from:
- **OSHA.gov**: https://www.osha.gov/data
- **Data.gov**: https://catalog.data.gov/dataset?organization=osha
- **Direct downloads**: Usually available as CSV files

### **2. Place Data in Raw Folder**

```bash
# Copy your data to the raw folder
cp your_osha_data.csv ../data/osha/raw/
```

### **3. Process the Data**

#### **Option A: Auto-detect (Recommended)**
```bash
python3 process_osha_data.py ../data/osha/raw/your_osha_data.csv
```

#### **Option B: Specify Data Type**
```bash
# For SIR data
python3 process_osha_data.py ../data/osha/raw/sir_data.csv --type sir

# For fatality data
python3 process_osha_data.py ../data/osha/raw/fatality_data.csv --type fatality
```

### **4. Import to Database**

```bash
# Validate first
python3 csv_importer.py ../data/osha/processed/your_osha_data_processed.csv --validate-only

# Import the data
python3 csv_importer.py ../data/osha/processed/your_osha_data_processed.csv
```

## 📁 **File Structure**

```
data/osha/
├── raw/                    # Put your original CSV files here
│   ├── sir_data.csv
│   ├── fatality_data.csv
│   └── inspection_data.csv
├── processed/              # Processed files (auto-generated)
│   ├── sir_data_processed.csv
│   ├── fatality_data_processed.csv
│   └── inspection_data_processed.csv
└── README.md
```

## 🔧 **Data Format Requirements**

### **Minimum Required Fields**
Your CSV must have these columns (names can vary):
- **Company/Employer name**
- **State**
- **Date** (incident date, fatality date, etc.)

### **Optional Fields**
- Address, City, Zip Code
- Latitude/Longitude coordinates
- NAICS codes
- Incident descriptions
- Industry classifications

### **Column Name Flexibility**
Our processor automatically maps common column names:

| **Our Schema** | **SIR Data** | **Fatality Data** | **Other Names** |
|----------------|---------------|-------------------|-----------------|
| `company_name` | `Employer` | `Employer` | `Company`, `Establishment` |
| `incident_date` | `EventDate` | `FatalityDate` | `Date`, `AccidentDate` |
| `address` | `Address1` | `Address` | `Street`, `Location` |
| `latitude` | `Latitude` | `Latitude` | `Lat`, `Y_Coordinate` |
| `longitude` | `Longitude` | `Longitude` | `Long`, `Lng`, `X_Coordinate` |

## 📊 **Processing Examples**

### **Example 1: SIR Data**
```bash
# Download SIR data from OSHA
# Place in: ../data/osha/raw/sir_data_2024.csv

# Process with auto-detection
python3 process_osha_data.py ../data/osha/raw/sir_data_2024.csv

# Import to database
python3 csv_importer.py ../data/osha/processed/sir_data_2024_processed.csv
```

### **Example 2: Fatality Data**
```bash
# Download fatality data from OSHA
# Place in: ../data/osha/raw/fatality_data_2024.csv

# Process with auto-detection
python3 process_osha_data.py ../data/osha/raw/fatality_data_2024.csv

# Import to database
python3 csv_importer.py ../data/osha/processed/fatality_data_2024_processed.csv
```

### **Example 3: Mixed Data Types**
```bash
# Process multiple files
python3 process_osha_data.py ../data/osha/raw/sir_data.csv
python3 process_osha_data.py ../data/osha/raw/fatality_data.csv

# Import all processed files
python3 csv_importer.py ../data/osha/processed/sir_data_processed.csv
python3 csv_importer.py ../data/osha/processed/fatality_data_processed.csv
```

## 🔍 **Data Validation**

### **Before Import**
```bash
# Check data quality
python3 csv_importer.py ../data/osha/processed/your_data_processed.csv --validate-only
```

### **Validation Checks**
- Required fields present
- Date format compatibility
- Coordinate validity
- Data type consistency

## 📈 **Database Integration**

### **Combined Analysis**
Once imported, you can analyze:
- **SIR + Fatality data** together
- **Industry trends** across incident types
- **Geographic patterns** for all incidents
- **Temporal analysis** of workplace safety

### **Query Examples**
```sql
-- Total incidents by type
SELECT incident_type, COUNT(*) as count 
FROM workplace_incidents 
GROUP BY incident_type;

-- Fatalities vs Injuries by industry
SELECT industry, 
       COUNT(CASE WHEN incident_type = 'fatality' THEN 1 END) as fatalities,
       COUNT(CASE WHEN incident_type != 'fatality' THEN 1 END) as injuries
FROM workplace_incidents 
GROUP BY industry;
```

## 🛠️ **Troubleshooting**

### **Common Issues**

#### **1. Column Mapping Errors**
**Problem**: "Column not found" errors
**Solution**: Check column names in your CSV and update mappings if needed

#### **2. Date Format Issues**
**Problem**: Date parsing errors
**Solution**: Our processor handles multiple formats automatically

#### **3. Coordinate Issues**
**Problem**: Invalid latitude/longitude
**Solution**: Records with invalid coordinates are still imported (coordinates set to NULL)

#### **4. Database Import Errors**
**Problem**: Import fails
**Solution**: 
1. Validate data first: `--validate-only`
2. Check database schema
3. Ensure all required fields are present

### **Debug Mode**
```bash
# Enable verbose logging
export PYTHONPATH=.
python3 -u process_osha_data.py your_file.csv
```

## 📚 **Advanced Usage**

### **Custom Column Mappings**
Edit `process_osha_data.py` to add custom column mappings:

```python
'custom_data': {
    'CustomID': 'osha_id',
    'CustomCompany': 'company_name',
    # ... add your mappings
}
```

### **Batch Processing**
```bash
# Process multiple files at once
for file in ../data/osha/raw/*.csv; do
    echo "Processing $file..."
    python3 process_osha_data.py "$file"
done
```

### **Data Quality Reports**
```bash
# Generate processing reports
python3 process_osha_data.py your_file.csv > processing_report.txt
```

## 🎯 **Best Practices**

1. **Always validate** before importing
2. **Keep original files** in raw folder
3. **Review processed data** before import
4. **Use descriptive filenames** for easy identification
5. **Backup database** before large imports
6. **Test with small samples** first

## 📞 **Support**

If you encounter issues:
1. Check the logs for error messages
2. Verify your CSV format matches requirements
3. Ensure all required fields are present
4. Test with a small sample of your data

## 🚀 **Next Steps**

After processing your data:
1. **Start your application** to see the new data
2. **Test the map view** with real incident markers
3. **Explore statistics** with actual workplace data
4. **Use filters** to analyze specific industries, states, or time periods

Your WorkerBooBoo application will now have **real OSHA data** powering workplace safety insights! 🏭📊✨
