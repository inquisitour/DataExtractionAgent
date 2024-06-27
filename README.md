DataExtractionAgent Project
Overview
This project involves extracting question-answer pairs related to ophthalmology from multiple web pages and saving them in a CSV file. It utilizes web scraping techniques and ensures the extracted data is relevant and properly processed.

Files Structure
agent.py: Main script for initiating crawling and saving data to CSV.
dataextraction.py: Handles asynchronous web crawling, HTML parsing, and extraction of QA pairs.
preprocessing.py: Contains functions for text cleaning, answer truncation, filtering irrelevant sentences, and API integration.
visualization.py: Saves extracted QA pairs to a CSV file.
Changes Made
Outlined below are the updates and modifications made to each file in the project:

agent.py
Purpose: Orchestrates the crawling process for specified URLs using asyncio and aiohttp, managing the initiation of data extraction and CSV saving.

Key Functions:

main(): Executes the main crawling and saving process.
dataextraction.py
Purpose: Handles asynchronous web crawling, HTML parsing, and extraction of QA pairs related to ophthalmology.

Key Functions:

fetch_page(session, url): Fetches the content of a web page given its URL using aiohttp. Utilizes asynchronous HTTP requests to retrieve HTML content and implements error handling to manage request failures.

extract_questions_answers(soup): Extracts question-answer pairs from parsed HTML content using BeautifulSoup. Identifies relevant content based on HTML tags (h1, h2, p, li, etc.). Cleans extracted text using functions from preprocessing.py.

is_valid_ophthalmology_question(question): Validates if a question pertains to ophthalmology based on specific keywords to ensure relevance of extracted QA pairs.

process_url(url, session, visited_urls, depth, seen_qa_pairs): Processes a URL to extract QA pairs and recursively crawls subpages within a specified depth limit. Initiates fetching of page content, extracts QA pairs using extract_questions_answers, and recursively processes subpages.

crawl(urls, depth=2): Initiates crawling of multiple URLs to extract ophthalmology-related QA pairs using asyncio. Manages concurrent crawling tasks, integrating functions for URL processing, QA pair extraction, and subpage crawling.

preprocessing.py
Purpose: Contains functions for text cleaning, answer truncation, filtering irrelevant sentences, and API integration for text preprocessing.

Key Functions:

clean_text(text): Cleans text by removing unwanted patterns and ensuring proper spacing.
truncate_answer(answer): Truncates answers to a maximum number of words for uniformity.
call_scrapegraphai_api(text): Calls ScrapeGraphAI API to clean and preprocess the text.
filter_irrelevant_sentences(text): Filters out irrelevant sentences from the text.
visualization.py
Purpose: Saves extracted QA pairs to a CSV file using Python's csv module, ensuring proper formatting and encoding.

Key Functions:

save_to_csv(data, filename): Saves the question-answer pairs to a CSV file.
Running the Program
Execute the main script to start the crawling process and save extracted QA pairs:

python3 agent.py









