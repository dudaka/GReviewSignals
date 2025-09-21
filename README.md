# GReviewSignals

**GReviewSignals** is a Python-based tool for analyzing Google Business Profile reviews from Google Takeout data. It extracts person names mentioned in reviews using Named Entity Recognition (NER) and provides comprehensive filtering and export capabilities.

## 🔍 Purpose

This tool helps business owners analyze their Google reviews to:

- **Track Staff Recognition**: Identify which staff members are frequently mentioned in positive reviews
- **Generate Reports**: Create monthly or custom time period analysis reports
- **Export Data**: Save analysis results to CSV for further processing
- **Marketing Insights**: Use real customer feedback to highlight top-performing team members
- **Performance Analytics**: Monitor trends in customer satisfaction and staff mentions over time

## ✨ Features

### Core Analysis

- **Smart Review Loading**: Automatically finds and loads all `reviews*.json` files from Google Takeout data
- **Advanced Filtering**: Filter reviews by:
  - Year and month
  - Star ratings (1-5 stars)
  - Custom date ranges
- **Name Extraction**: Uses spaCy NLP to extract person names from review comments with high accuracy
- **Comprehensive Reporting**: Detailed analysis with mention counts and statistics

### Export & Organization

- **CSV Export**: Export both filtered reviews and name analysis to CSV files
- **Organized Output**: All exports automatically saved to `output/` directory
- **Excel Compatible**: CSV files ready for use in Excel, Google Sheets, or other tools
- **Flexible Paths**: Configurable data and output directories

### User Experience

- **Command Line Interface**: Easy-to-use CLI with comprehensive options
- **Progress Feedback**: Clear status updates and error handling
- **Help & Examples**: Built-in help with usage examples
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🛠️ Installation

### Prerequisites

- Python 3.7+
- Google Business Profile data from Google Takeout

### Setup

```bash
# Clone the repository
git clone https://github.com/dudaka/GReviewSignals.git
cd GReviewSignals

# Create conda environment from environment.yml
conda env create -f environment.yml

# Activate the environment
conda activate greview-signals

# Download spaCy English model for name recognition
python -m spacy download en_core_web_sm
```

### Alternative Installation Methods

```bash
# Manual conda installation
conda install -c conda-forge spacy pandas jupyter
python -m spacy download en_core_web_sm

# Or minimal conda installation (without pandas and jupyter)
conda install -c conda-forge spacy
python -m spacy download en_core_web_sm

# Using pip (if preferred)
pip install spacy pandas jupyter
python -m spacy download en_core_web_sm
```

## 📁 Data Preparation

1. **Request Google Takeout Data**:

   - Go to [Google Takeout](https://takeout.google.com)
   - Select "My Business Profile" or "Google Business Profile"
   - Download the ZIP file(s)

2. **Extract Data**:
   ```bash
   # Extract to the data directory
   mkdir data
   cd data
   unzip your-takeout-file.zip
   # Should create: data/Takeout/Google Business Profile/...
   ```

## 🚀 Usage

### Command Line Interface

#### Basic Analysis

```bash
# Analyze all reviews
python main.py

# Filter by specific time period
python main.py --year 2025 --month 8

# Filter by star ratings (high ratings only)
python main.py --stars FOUR FIVE
```

#### Export to CSV

```bash
# Export reviews to CSV
python main.py --export-reviews reviews.csv

# Export name analysis to CSV
python main.py --export-names staff_mentions.csv

# Export both with filtering
python main.py --year 2025 --month 8 --stars FOUR FIVE \
  --export-reviews august_reviews.csv \
  --export-names august_staff.csv
```

#### Advanced Options

```bash
# Show actual review content
python main.py --year 2025 --stars FIVE --show-reviews

# Use custom directories
python main.py --data-dir /path/to/takeout --output-dir /path/to/results

# Comprehensive analysis with all features
python main.py --year 2025 --month 8 --stars FOUR FIVE \
  --show-reviews --max-reviews 20 \
  --export-reviews detailed_reviews.csv \
  --export-names top_staff.csv \
  --output-dir monthly_reports
```

### Python Module Usage

You can also use GReviewSignals as a Python module in your own scripts:

```python
from greview_signals.analyzer import GoogleBusinessProfileAnalyzer

# Initialize the analyzer
analyzer = GoogleBusinessProfileAnalyzer(
    data_dir="data",
    output_dir="output"
)

# Run analysis with filtering
filtered_reviews, name_counts = analyzer.analyze(
    year=2025,
    month=8,
    star_ratings=['FOUR', 'FIVE'],
    export_reviews_csv="august_reviews.csv",
    export_names_csv="august_staff.csv"
)

# Process results
print(f"Found {len(filtered_reviews)} reviews")
print(f"Top mentioned staff: {sorted(name_counts.items(), key=lambda x: -x[1])[:5]}")

# Export additional formats or do custom processing
analyzer.export_reviews_to_csv(filtered_reviews, "custom_export.csv")
```

#### Module API Reference

**Core Methods:**

- `load_reviews()`: Load all reviews from Google Takeout data
- `filter_reviews(year, month, star_ratings)`: Filter reviews by criteria
- `extract_person_names(reviews)`: Extract person names using NER
- `analyze()`: Complete analysis pipeline with optional exports

**Export Methods:**

- `export_reviews_to_csv(reviews, filename)`: Export review data to CSV
- `export_name_analysis_to_csv(name_counts, filename)`: Export name analysis to CSV

## 📊 Output Files

### Reviews CSV (`reviews.csv`)

Contains filtered review data with columns:

- `review_id`: Unique review identifier
- `reviewer_name`: Customer name
- `star_rating`: Rating (ONE, TWO, THREE, FOUR, FIVE)
- `comment`: Full review text
- `create_time`: Review creation date
- `update_time`: Last update date
- `reviewer_photo_url`: Customer profile photo
- `review_reply`: Business owner response

### Names CSV (`names.csv`)

Contains staff mention analysis:

- `person_name`: Name extracted from reviews
- `mention_count`: Number of reviews mentioning this person

## 🗂️ Project Structure

```
GReviewSignals/
├── data/                          # Google Takeout data
│   └── Takeout/
│       └── Google Business Profile/
│           ├── account-*/
│           └── location-*/
│               ├── reviews*.json
│               └── data.json
├── output/                        # Generated reports (auto-created)
│   ├── reviews.csv
│   └── names.csv
├── greview_signals/               # Python package
│   ├── __init__.py               # Package initialization
│   └── analyzer.py               # Core GoogleBusinessProfileAnalyzer class
├── notebooks/
│   └── analyzing.ipynb           # Jupyter notebook for exploration
├── main.py                       # Main CLI application
└── README.md
```

## 📋 Command Line Options

| Option             | Description                    | Example                        |
| ------------------ | ------------------------------ | ------------------------------ |
| `--data-dir`       | Google Takeout data directory  | `--data-dir data`              |
| `--output-dir`     | Output directory for CSV files | `--output-dir results`         |
| `--year`           | Filter by year                 | `--year 2025`                  |
| `--month`          | Filter by month (1-12)         | `--month 8`                    |
| `--stars`          | Filter by star ratings         | `--stars FOUR FIVE`            |
| `--show-reviews`   | Display review content         | `--show-reviews`               |
| `--max-reviews`    | Max reviews to display         | `--max-reviews 20`             |
| `--export-reviews` | Export reviews to CSV          | `--export-reviews reviews.csv` |
| `--export-names`   | Export name analysis to CSV    | `--export-names names.csv`     |

## 🔬 Analysis Methodology

1. **Data Loading**: Recursively finds all `reviews*.json` files in the Google Takeout structure
2. **Filtering**: Applies date and rating filters to focus on relevant reviews
3. **Name Extraction**: Uses spaCy's Named Entity Recognition to identify PERSON entities
4. **Deduplication**: Counts unique mentions per person across all filtered reviews
5. **Ranking**: Sorts results by mention frequency for easy identification of top performers

## 🎯 Use Cases

### Monthly Staff Recognition

```bash
# Generate monthly report for August 2025
python main.py --year 2025 --month 8 --stars FOUR FIVE \
  --export-reviews august_positive_reviews.csv \
  --export-names august_staff_mentions.csv
```

### Quarterly Analysis

```bash
# Analyze Q3 2025 (July-September)
for month in 7 8 9; do
  python main.py --year 2025 --month $month --stars FOUR FIVE \
    --export-names "q3_month_${month}_staff.csv"
done
```

### Marketing Material Generation

```bash
# Get 5-star reviews with staff mentions for marketing
python main.py --stars FIVE --show-reviews --max-reviews 50 \
  --export-reviews five_star_reviews.csv
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## � License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🛟 Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/dudaka/GReviewSignals/issues)
- **Documentation**: Check this README and inline help (`python main.py --help`)
- **Examples**: See the `notebooks/` directory for Jupyter notebook examples

## 🔮 Future Enhancements

- Sentiment analysis for review tone
- Time-series visualization of staff mentions
- Integration with other review platforms
- Automated report scheduling
- Web dashboard interface
