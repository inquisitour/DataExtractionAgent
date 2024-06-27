# DataExtractionAgent Project

## Overview
This project involves extracting question-answer pairs related to ophthalmology from multiple web pages and saving them in a CSV file. It utilizes web scraping techniques and ensures the extracted data is relevant and properly processed.

## Files Structure
- **`agent.py`**: Main script for initiating crawling and saving data to CSV.
- **`dataextraction.py`**: Handles asynchronous web crawling, HTML parsing, and extraction of QA pairs.
- **`preprocessing.py`**: Contains functions for text cleaning, answer truncation, filtering irrelevant sentences, and API integration.
- **`visualization.py`**: Saves extracted QA pairs to a CSV file.

## Usage in Project

### `agent.py`
**Purpose**: Orchestrates the crawling process for specified URLs using `asyncio` and `aiohttp`, managing the initiation of data extraction and CSV saving.

**Where used**: 
- `main()` function is called to start the crawling process and save the extracted QA pairs to a CSV file.

### `dataextraction.py`
**Purpose**: Handles asynchronous web crawling, HTML parsing, and extraction of QA pairs related to ophthalmology.

**Where used**:
- `fetch_page(session, url)`: Used in `process_url()` to fetch HTML content asynchronously from web pages.
- `extract_questions_answers(soup)`: Used in `process_url()` to parse HTML content and extract QA pairs.
- `is_valid_ophthalmology_question(question)`: Used in `extract_questions_answers()` to validate if a question pertains to ophthalmology.
- `process_url(url, session, visited_urls, depth, seen_qa_pairs)`: Used in `crawl()` to process URLs recursively and extract QA pairs.

### `preprocessing.py`
**Purpose**: Contains functions for text cleaning, answer truncation, filtering irrelevant sentences, and API integration for text preprocessing.

**Where used**:
- All functions (`clean_text()`, `truncate_answer()`, `call_scrapegraphai_api()`, `filter_irrelevant_sentences()`) are used in `extract_questions_answers()` in `dataextraction.py` to clean and process extracted text before saving to CSV.

### `visualization.py`
**Purpose**: Saves extracted QA pairs to a CSV file using Python's `csv` module, ensuring proper formatting and encoding.

**Where used**:
- `save_to_csv(data, filename)`: Called in `agent.py`'s `main()` function to save QA pairs extracted from web pages to a CSV file.

## Running the Program
Execute the main script to start the crawling process and save extracted QA pairs:
```bash
python3 agent.py
