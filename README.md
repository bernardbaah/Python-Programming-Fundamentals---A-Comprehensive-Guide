# Python Programming Fundamentals — A Comprehensive Guide

**Author:** Bernard Baah  
**Series:** Filly Coder

A web-based reader for *Python Programming Fundamentals: A Comprehensive Guide* — now fully expanded to **414 pages** across **25 chapters**, with exercises, key concepts, and chapter summaries throughout.

## Running Locally

**Requirements:** Python 3.13+

```bash
# Install dependencies
pip install flask pymupdf

# Place the book PDF in book_data/ as:
# book_data/Python_Fundamentals_Interior.pdf

# Start the server
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Project Structure

```
├── app.py                              # Flask web server
├── viewer.html                         # PDF viewer UI (page-flip, zoom, search)
├── pyproject.toml                      # Python dependencies
├── book_data/
│   ├── Python_Fundamentals_Interior.pdf   # 414-page KDP-ready PDF
│   ├── Python_Fundamentals_Interior.docx  # Source DOCX
│   └── chapter_XX.json                 # Per-chapter structured data
└── .agents/scripts/
    ├── build_book_elegant.py           # Build DOCX from chapter JSON
    └── build_pdf_elegant.py            # Render DOCX → KDP-ready PDF
```

## Chapter Structure (25 Chapters · 414 Pages)

| # | Chapter |
|---|---------|
| 1 | Introduction to Python |
| 2 | Getting Started with Python |
| 3 | Variables and Data Types |
| 4 | Control Structures |
| 5 | Functions |
| 6 | Modules and Libraries |
| 7 | File Handling |
| 8 | Exception Handling |
| 9 | Data Structures |
| 10 | Object-Oriented Programming: Basics |
| 11 | Object-Oriented Programming: Advanced Concepts |
| 12 | Error Handling and Debugging |
| 13 | Working with Files and Directories (Part 2) |
| 14 | Introduction to Testing |
| 15 | Introduction to Modules and Packages |
| 16 | Advanced Modules and Packages |
| 17 | Working with External APIs |
| 18 | Introduction to Web Development with Flask |
| 19 | Intermediate Flask Development |
| 20 | Introduction to Data Visualization with Matplotlib |
| 21 | Advanced Data Visualization with Seaborn |
| 22 | Introduction to Machine Learning with scikit-learn |
| 23 | Web Scraping with Python |
| 24 | Python Automation |
| 25 | Conclusion and Next Steps |

Each chapter includes:
- **125 total exercises** across the book
- **Key concepts** summary
- **Chapter summary**
- **Contextual images** (250+ total)

## About the Book

A comprehensive introduction to Python programming covering syntax and semantics, data structures and algorithms, file I/O, exceptions, debugging, web development, data visualization, machine learning, and automation.

Ideal for beginners, students, and professionals seeking a solid foundation in Python.

---

*© Bernard Baah / Filly Coder. All rights reserved.*
