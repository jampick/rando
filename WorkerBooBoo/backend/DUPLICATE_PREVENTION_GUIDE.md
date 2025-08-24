# 🚫 Duplicate Prevention Guide

## Overview
The Enhanced CSV Importer automatically prevents duplicate records during data imports using multiple detection strategies.

## 🔍 How Duplicate Detection Works

### 1. **OSHA ID Matching (Most Reliable)**
- Checks if `osha_id` already exists in database
- **100% accurate** - if OSHA ID exists, it's definitely a duplicate

### 2. **Company + Location + Date**
- Checks combination of: Company Name + City + State + Incident Date
- **High accuracy** - same company, same location, same date = likely duplicate

### 3. **Company + Incident Type + Date**
- Checks combination of: Company Name + Incident Type + Incident Date
- **Medium accuracy** - useful when location data is missing

### 4. **Address + Coordinates**
- Checks combination of: Address + Latitude + Longitude
- **High accuracy** - exact same location = likely duplicate

## 🚀 Usage Examples

### Basic Import (Skip Duplicates)
```bash
# Import new data, skip any duplicates
python3 enhanced_csv_importer.py your_data.csv

# Import with specific duplicate strategy
python3 enhanced_csv_importer.py your_data.csv --duplicate-strategy osha_id
```

### Update Existing Records
```bash
# Update existing records instead of skipping
python3 enhanced_csv_importer.py your_data.csv --update-existing

# Update with specific strategy
python3 enhanced_csv_importer.py your_data.csv --update-existing --duplicate-strategy company_location_date
```

### Custom Batch Size
```bash
# Process in smaller batches (useful for large files)
python3 enhanced_csv_importer.py your_data.csv --batch-size 500
```

### Export Template
```bash
# Generate a template CSV file
python3 enhanced_csv_importer.py --export-template
```

## 📊 What Happens During Import

### 1. **Duplicate Detection Phase**
```
🔍 Detecting duplicates using strategy: all
✅ Duplicate detection complete:
   Unique records: 1,234
   Duplicate records: 56
```

### 2. **Import Phase**
```
📦 Processing batch 1/5 (1,000 records)
💾 Committed batch 1
📦 Processing batch 2/5 (1,000 records)
💾 Committed batch 2
...
```

### 3. **Final Summary**
```
🎯 IMPORT SUMMARY:
   📋 Total processed: 1,234
   ✅ New records imported: 1,178
   🔄 Existing records updated: 0
   ⏭️  Duplicates skipped: 56
   ❌ Errors: 0
```

## 🎯 Duplicate Detection Strategies

### `--duplicate-strategy all` (Default)
- Uses **all 4 strategies** for maximum accuracy
- **Best for**: Production imports, data quality critical

### `--duplicate-strategy osha_id`
- Only checks OSHA ID matches
- **Best for**: Clean data with reliable OSHA IDs

### `--duplicate-strategy company_location_date`
- Checks Company + Location + Date combinations
- **Best for**: Data without OSHA IDs but with good location info

### `--duplicate-strategy company_incident_type`
- Checks Company + Incident Type + Date combinations
- **Best for**: Data with missing location information

### `--duplicate-strategy address_coordinates`
- Checks Address + Coordinates combinations
- **Best for**: Data with precise address and coordinate information

## 🔄 Update vs. Skip Behavior

### Default Behavior (Skip Duplicates)
- **New records**: ✅ Imported
- **Duplicate records**: ⏭️ Skipped
- **Existing records**: 🔒 Unchanged

### With `--update-existing` Flag
- **New records**: ✅ Imported
- **Duplicate records**: 🔄 Updated with new data
- **Existing records**: 🔄 Updated if matching

## 💡 Best Practices

### 1. **Always Use `--update-existing` for Data Updates**
```bash
# When updating existing data
python3 enhanced_csv_importer.py updated_data.csv --update-existing
```

### 2. **Use Appropriate Duplicate Strategy**
```bash
# For clean OSHA data
python3 enhanced_csv_importer.py osha_data.csv --duplicate-strategy osha_id

# For data without OSHA IDs
python3 enhanced_csv_importer.py other_data.csv --duplicate-strategy company_location_date
```

### 3. **Monitor Import Results**
- Check the import summary for any errors
- Verify duplicate counts make sense
- Use smaller batch sizes for large files if memory issues occur

### 4. **Backup Before Large Imports**
```bash
# Backup your database before large imports
cp workplace_safety.db workplace_safety_backup_$(date +%Y%m%d).db
```

## 🚨 Common Scenarios

### Scenario 1: Monthly Data Updates
```bash
# Update existing records with new information
python3 enhanced_csv_importer.py monthly_update.csv --update-existing
```

### Scenario 2: New Data Source
```bash
# Import new data, skip any duplicates
python3 enhanced_csv_importer.py new_source.csv
```

### Scenario 3: Data Cleanup
```bash
# Re-import cleaned data, update existing
python3 enhanced_csv_importer.py cleaned_data.csv --update-existing
```

## 🔧 Troubleshooting

### High Duplicate Counts
- Check if your data source has changed
- Verify duplicate detection strategy is appropriate
- Consider using `--update-existing` if you want to update records

### Import Errors
- Check CSV format and column names
- Verify database connection
- Use smaller batch sizes for large files

### Memory Issues
- Reduce batch size: `--batch-size 500`
- Process files in smaller chunks
- Check available system memory

## 📈 Performance Tips

- **Batch size**: 1000 records per batch (default) works well for most cases
- **Duplicate strategy**: Use `osha_id` for fastest processing if available
- **Database**: Ensure adequate disk space and memory for large imports
- **Monitoring**: Watch import progress and adjust batch size if needed

---

**Remember**: The duplicate prevention system is designed to protect your data integrity while providing flexibility for different import scenarios. Choose the strategy that best fits your data quality and requirements.
