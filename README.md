# GReviewSignals

**GReviewSignals** is a Python-based tool to extract human names (nail technicians) mentioned in **4- and 5-star Google Reviews** during a specific time window (e.g., April 2025).

## 🔍 Purpose

This tool helps nail salon business owners track which staff members are frequently praised by customers in positive Google reviews. This can be used to:

- Recognize top-performing staff
- Generate monthly praise reports
- Boost marketing with real customer feedback

## 📦 Features

- Parses multiple `reviews*.json` files exported from Google
- Filters by star rating and date
- Uses spaCy NLP to extract person names from review comments
- Counts how many reviews mention each name
- Outputs human-readable summaries

## 🛠️ Installation

```bash
git clone https://github.com/dudaka/GReviewSignals.git
cd GReviewSignals
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```
