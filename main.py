#!/usr/bin/env python3
"""
Google Business Profile Review Analyzer - Command Line Interface

This is the main entry point for the GReviewSignals application. It provides
a command-line interface to the GoogleBusinessProfileAnalyzer class for analyzing
Google Business Profile reviews from Google Takeout data.

The CLI supports:
- Filtering reviews by date and star rating
- Exporting analysis results to CSV files
- Displaying review content
- Configurable input and output directories

Usage:
    python main.py [OPTIONS]

Examples:
    python main.py --year 2025 --month 8 --stars FOUR FIVE
    python main.py --export-reviews reviews.csv --export-names names.csv
    python main.py --help

Requirements:
    - spacy with en_core_web_sm model
    - pandas (optional)
    - Google Takeout data in data/ directory
"""

import sys
import argparse

from greview_signals.analyzer import GoogleBusinessProfileAnalyzer

def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Analyze Google Business Profile reviews from Takeout data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Analyze all reviews
  python main.py --year 2025 --month 8             # Filter by August 2025
  python main.py --stars FOUR FIVE                 # Only 4-5 star reviews
  python main.py --year 2025 --stars FIVE --show-reviews  # Show filtered reviews
  python main.py --export-reviews reviews.csv      # Export reviews to output/reviews.csv
  python main.py --export-names names.csv          # Export name analysis to output/names.csv
  python main.py --year 2025 --export-reviews reviews_2025.csv --export-names names_2025.csv
  python main.py --output-dir results              # Use custom output directory
  python main.py --data-dir /path/to/data --output-dir /path/to/output
        """
    )
    
    parser.add_argument("--data-dir", default="data",
                       help="Directory containing Google Takeout data (default: data)")
    parser.add_argument("--output-dir", default="output",
                       help="Directory for output CSV files (default: output)")
    parser.add_argument("--year", type=int,
                       help="Filter reviews by year (e.g., 2025)")
    parser.add_argument("--month", type=int, choices=range(1, 13),
                       help="Filter reviews by month (1-12)")
    parser.add_argument("--stars", nargs="+", 
                       choices=["ONE", "TWO", "THREE", "FOUR", "FIVE"],
                       help="Filter by star ratings (e.g., --stars FOUR FIVE)")
    parser.add_argument("--show-reviews", action="store_true",
                       help="Display the filtered reviews")
    parser.add_argument("--max-reviews", type=int, default=10,
                       help="Maximum number of reviews to display (default: 10)")
    parser.add_argument("--export-reviews", type=str,
                       help="Export filtered reviews to CSV file (e.g., reviews.csv)")
    parser.add_argument("--export-names", type=str,
                       help="Export name analysis to CSV file (e.g., names.csv)")
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = GoogleBusinessProfileAnalyzer(data_dir=args.data_dir, output_dir=args.output_dir)
    
    # Run analysis
    try:
        filtered_reviews, name_counts = analyzer.analyze(
            year=args.year,
            month=args.month,
            star_ratings=args.stars,
            show_reviews=args.show_reviews,
            max_reviews=args.max_reviews,
            export_reviews_csv=args.export_reviews,
            export_names_csv=args.export_names
        )
        
        if name_counts:
            print(f"\n✅ Analysis complete! Found {len(name_counts)} unique names in {len(filtered_reviews)} reviews.")
        else:
            print(f"\n⚠️  No names extracted from {len(filtered_reviews)} reviews.")
            
    except KeyboardInterrupt:
        print("\n\n🛑 Analysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()