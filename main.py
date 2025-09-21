#!/usr/bin/env python3
"""
Google Business Profile Review Analyzer

This script analyzes Google Business Profile reviews from Google Takeout data.
It extracts person names mentioned in reviews using Named Entity Recognition (NER)
and provides filtering options by date and star rating.

Usage:
    python main.py [OPTIONS]

Requirements:
    pip install spacy
    python -m spacy download en_core_web_sm
"""

import json
import glob
import argparse
import sys
import csv
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Tuple, Optional

try:
    import spacy
except ImportError:
    print("Error: spacy is required. Install it with: pip install spacy")
    print("Then download the English model with: python -m spacy download en_core_web_sm")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("Warning: pandas not found. CSV export will use basic CSV writer.")
    pd = None


class GoogleBusinessProfileAnalyzer:
    """Analyzer for Google Business Profile reviews from Takeout data."""
    
    def __init__(self, data_dir: str = "data", output_dir: str = "output"):
        """
        Initialize the analyzer.
        
        Args:
            data_dir: Directory containing the extracted Google Takeout data
            output_dir: Directory for output files (CSV exports)
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.takeout_dir = self.data_dir / "Takeout" / "Google Business Profile"
        self.reviews = []
        self.nlp = None
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
    def load_spacy_model(self) -> bool:
        """
        Load the spaCy English model for NER.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.nlp = spacy.load("en_core_web_sm")
            return True
        except OSError:
            print("Error: spaCy English model not found.")
            print("Please install it with: python -m spacy download en_core_web_sm")
            return False
    
    def load_reviews(self) -> int:
        """
        Load all reviews from the Google Takeout data.
        
        Returns:
            Number of reviews loaded
        """
        print(f"Loading reviews from: {self.takeout_dir}")
        
        if not self.takeout_dir.exists():
            print(f"Error: Takeout directory not found at {self.takeout_dir}")
            print("Please ensure you have extracted the Google Takeout data to the data folder.")
            return 0
        
        # Find all review files
        review_files = list(self.takeout_dir.glob('**/reviews*.json'))
        print(f"Found {len(review_files)} review files")
        
        self.reviews = []
        for file_path in review_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Handle different review file formats
                if isinstance(data, dict):
                    if 'reviews' in data:
                        # Main reviews.json file with multiple reviews
                        reviews_in_file = data['reviews']
                        self.reviews.extend(reviews_in_file)
                    else:
                        # Individual review file
                        self.reviews.append(data)
                elif isinstance(data, list):
                    # List of reviews
                    self.reviews.extend(data)
                    
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"Warning: Error reading {file_path}: {e}")
                continue
        
        print(f"Total reviews loaded: {len(self.reviews)}")
        return len(self.reviews)
    
    def filter_reviews(self, 
                      year: Optional[int] = None, 
                      month: Optional[int] = None,
                      star_ratings: Optional[List[str]] = None) -> List[Dict]:
        """
        Filter reviews by date and star rating.
        
        Args:
            year: Filter by year (e.g., 2025)
            month: Filter by month (1-12)
            star_ratings: List of star ratings to include (e.g., ['FOUR', 'FIVE'])
        
        Returns:
            List of filtered reviews
        """
        filtered_reviews = []
        
        for review in self.reviews:
            # Filter by star rating
            if star_ratings:
                review_rating = review.get("starRating", "").upper()
                if review_rating not in star_ratings:
                    continue
            
            # Filter by date
            if year is not None or month is not None:
                update_time = review.get("updateTime")
                if update_time:
                    try:
                        dt = datetime.fromisoformat(update_time.replace('Z', '+00:00'))
                        if year is not None and dt.year != year:
                            continue
                        if month is not None and dt.month != month:
                            continue
                    except Exception as e:
                        print(f"Warning: Skipping review with invalid date: {update_time}, error: {e}")
                        continue
            
            filtered_reviews.append(review)
        
        return filtered_reviews
    
    def extract_person_names(self, reviews: List[Dict]) -> Dict[str, int]:
        """
        Extract person names mentioned in review comments using NER.
        
        Args:
            reviews: List of review dictionaries
        
        Returns:
            Dictionary mapping person names to mention counts
        """
        if not self.nlp:
            print("Error: spaCy model not loaded. Call load_spacy_model() first.")
            return {}
        
        name_to_review_ids = defaultdict(set)
        
        for review in reviews:
            comment = review.get("comment", "")
            if not comment:
                continue
                
            doc = self.nlp(comment)
            review_id = review.get("name", review.get("reviewId", "unknown"))
            
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name_to_review_ids[ent.text.strip()].add(review_id)
        
        # Convert to counts
        name_counts = {name: len(ids) for name, ids in name_to_review_ids.items()}
        return name_counts
    
    def print_reviews(self, reviews: List[Dict], max_reviews: int = 10):
        """
        Print reviews in a readable format.
        
        Args:
            reviews: List of review dictionaries
            max_reviews: Maximum number of reviews to print
        """
        print(f"\n{'='*80}")
        print(f"REVIEWS ({len(reviews)} total, showing first {min(max_reviews, len(reviews))})")
        print(f"{'='*80}")
        
        for i, review in enumerate(reviews[:max_reviews]):
            name = review.get("reviewer", {}).get("displayName", "Anonymous")
            stars = review.get("starRating", "N/A")
            comment = review.get("comment", "")
            time = review.get("updateTime", "")
            
            print(f"\n[{i+1}] {time} | {name} | {stars} stars")
            print(f"{comment}")
            print("-" * 60)
    
    def export_reviews_to_csv(self, reviews: List[Dict], filename: str):
        """
        Export reviews to CSV file in the output directory.
        
        Args:
            reviews: List of review dictionaries
            filename: Output CSV filename (will be saved in output directory)
        """
        if not reviews:
            print("No reviews to export.")
            return
        
        # Ensure filename is in output directory
        output_path = self.output_dir / filename
        
        if pd is not None:
            # Use pandas for better CSV handling
            review_data = []
            for review in reviews:
                reviewer = review.get("reviewer", {})
                review_data.append({
                    "review_id": review.get("reviewId", review.get("name", "")),
                    "reviewer_name": reviewer.get("displayName", "Anonymous"),
                    "star_rating": review.get("starRating", ""),
                    "comment": review.get("comment", ""),
                    "create_time": review.get("createTime", ""),
                    "update_time": review.get("updateTime", ""),
                    "reviewer_photo_url": reviewer.get("profilePhotoUrl", ""),
                    "review_reply": review.get("reviewReply", {}).get("comment", "") if review.get("reviewReply") else ""
                })
            
            df = pd.DataFrame(review_data)
            df.to_csv(output_path, index=False, encoding='utf-8')
        else:
            # Fallback to basic CSV writer
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["review_id", "reviewer_name", "star_rating", "comment", 
                             "create_time", "update_time", "reviewer_photo_url", "review_reply"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for review in reviews:
                    reviewer = review.get("reviewer", {})
                    writer.writerow({
                        "review_id": review.get("reviewId", review.get("name", "")),
                        "reviewer_name": reviewer.get("displayName", "Anonymous"),
                        "star_rating": review.get("starRating", ""),
                        "comment": review.get("comment", ""),
                        "create_time": review.get("createTime", ""),
                        "update_time": review.get("updateTime", ""),
                        "reviewer_photo_url": reviewer.get("profilePhotoUrl", ""),
                        "review_reply": review.get("reviewReply", {}).get("comment", "") if review.get("reviewReply") else ""
                    })
        
        print(f"✅ Exported {len(reviews)} reviews to {output_path}")
    
    def export_name_analysis_to_csv(self, name_counts: Dict[str, int], filename: str):
        """
        Export name analysis results to CSV file in the output directory.
        
        Args:
            name_counts: Dictionary mapping names to mention counts
            filename: Output CSV filename (will be saved in output directory)
        """
        if not name_counts:
            print("No name analysis data to export.")
            return
        
        # Ensure filename is in output directory
        output_path = self.output_dir / filename
        
        if pd is not None:
            # Use pandas for better CSV handling
            df = pd.DataFrame([
                {"person_name": name, "mention_count": count}
                for name, count in sorted(name_counts.items(), key=lambda x: -x[1])
            ])
            df.to_csv(output_path, index=False, encoding='utf-8')
        else:
            # Fallback to basic CSV writer
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["person_name", "mention_count"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for name, count in sorted(name_counts.items(), key=lambda x: -x[1]):
                    writer.writerow({
                        "person_name": name,
                        "mention_count": count
                    })
        
        print(f"✅ Exported {len(name_counts)} unique names to {output_path}")
    
    def analyze(self, 
                year: Optional[int] = None,
                month: Optional[int] = None, 
                star_ratings: Optional[List[str]] = None,
                show_reviews: bool = False,
                max_reviews: int = 10,
                export_reviews_csv: Optional[str] = None,
                export_names_csv: Optional[str] = None) -> Tuple[List[Dict], Dict[str, int]]:
        """
        Run the complete analysis pipeline.
        
        Args:
            year: Filter by year
            month: Filter by month
            star_ratings: Filter by star ratings
            show_reviews: Whether to print the reviews
            max_reviews: Maximum number of reviews to print
            export_reviews_csv: Filename to export filtered reviews as CSV
            export_names_csv: Filename to export name analysis as CSV
        
        Returns:
            Tuple of (filtered_reviews, name_counts)
        """
        # Load data
        if not self.reviews:
            review_count = self.load_reviews()
            if review_count == 0:
                return [], {}
        
        # Load NLP model
        if not self.nlp:
            if not self.load_spacy_model():
                return [], {}
        
        # Filter reviews
        filtered_reviews = self.filter_reviews(year=year, month=month, star_ratings=star_ratings)
        
        # Print filter summary
        filter_parts = []
        if year:
            filter_parts.append(f"year={year}")
        if month:
            filter_parts.append(f"month={month}")
        if star_ratings:
            filter_parts.append(f"ratings={star_ratings}")
        
        filter_str = ", ".join(filter_parts) if filter_parts else "no filters"
        print(f"\nFiltered reviews ({filter_str}): {len(filtered_reviews)}")
        
        if not filtered_reviews:
            print("No reviews match the filter criteria.")
            return [], {}
        
        # Show reviews if requested
        if show_reviews:
            self.print_reviews(filtered_reviews, max_reviews)
        
        # Extract person names
        print(f"\nExtracting person names from {len(filtered_reviews)} reviews...")
        name_counts = self.extract_person_names(filtered_reviews)
        
        # Print results
        if name_counts:
            sorted_names = sorted(name_counts.items(), key=lambda x: -x[1])
            print(f"\n📌 Total unique names mentioned: {len(sorted_names)}")
            print(f"{'='*50}")
            for name, count in sorted_names:
                print(f"{name}: mentioned in {count} review(s)")
        else:
            print("No person names found in the reviews.")
        
        # Export to CSV if requested
        if export_reviews_csv:
            self.export_reviews_to_csv(filtered_reviews, export_reviews_csv)
        
        if export_names_csv:
            self.export_name_analysis_to_csv(name_counts, export_names_csv)
        
        return filtered_reviews, name_counts


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