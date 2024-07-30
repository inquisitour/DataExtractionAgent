# DataExtraction.py


import asyncio
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from cachetools import TTLCache
from preprocessing import Preprocessor  # Ensure this import path is correct
from visualization import DataVisualizer
import config
import logging
import csv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OphthalmologySpider(CrawlSpider):
    name = 'ophthalmology'
    allowed_domains = [
        'healthline.com',
        'healthdirect.gov.au',
        'med.unc.edu',
        'healthcare.utah.edu',
        'cdc.gov'
    ]

    start_urls = config.URLS_TO_SCRAPE

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(OphthalmologySpider, self).__init__(*args, **kwargs)
        self.crawled_items = []

    def parse_item(self, response):
        try:
            logger.info(f"Scraping URL: {response.url}")
            preprocessor = Preprocessor()
            
            # Extract questions and answers
            questions = response.css('h1::text, h2::text, h3::text, div a::text').getall()
            answers = response.css('p::text').getall()

            # Filter questions and answers
            filtered_questions = [q for q in questions if q.strip().endswith('?')]
            filtered_answers = [a for a in answers if a.strip().endswith('.')]

            scraped_count = 0
            # Iterate through extracted questions and answers
            for q, a in zip(filtered_questions, filtered_answers):
                cleaned_question, processed_answer = preprocessor.preprocess_qa_pair(q, a)
                if cleaned_question and processed_answer:
                    self.crawled_items.append({
                        'question': cleaned_question,
                        'answer': processed_answer
                    })
                    # Save directly to CSV
                    self.save_to_csv(cleaned_question, processed_answer)
                    scraped_count += 1
                else:
                    logger.warning(f"Skipped QA pair - Question: {q}, Answer: {a}")
            
            logger.info(f"Scraped {scraped_count} Q&A pairs from {response.url}")

        except Exception as e:
            logger.error(f"Error in parse_item: {e}")

    def save_to_csv(self, question, answer):
        with open(config.CSV_OUTPUT_PATH, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([question, answer])

class ScrapingManager:
    def __init__(self):
        # Initialize the cache with appropriate settings
        self.cache = TTLCache(maxsize=config.CACHE_MAXSIZE, ttl=config.CACHE_TTL)
        self.preprocessor = Preprocessor()
        self.visualizer = DataVisualizer()
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

    async def scrape_data(self, urls, depth=config.MAX_DEPTH):
        all_qa_pairs = []

        try:
            logger.info("Starting scraping process for all URLs...")
            # Check cache first and filter out URLs already in cache
            cached_results = [self.cache.get(url) for url in urls if url in self.cache]
            if cached_results:
                all_qa_pairs.extend([item for sublist in cached_results for item in sublist])
                urls = [url for url in urls if url not in self.cache]

            if urls:
                # Scrapy
                try:
                    process = CrawlerProcess(settings=config.SCRAPY_SETTINGS)
                    process.crawl(OphthalmologySpider)  # Pass the spider class
                    process.start()
                    # Adjusted to get crawled items from the spider
                    spider = next(iter(process.crawlers)).spider
                    all_qa_pairs.extend(spider.crawled_items)
                except Exception as e:
                    logger.error(f"Error occurred during Scrapy crawling: {e}")

                # Update cache with new results
                for url, result in zip(urls, all_qa_pairs):
                    self.cache[url] = result

            logger.info(f"Scraping process completed for all URLs. Total Q&A pairs scraped: {len(all_qa_pairs)}")

        except Exception as e:
            logger.error(f"Unexpected error occurred during scraping data: {e}")

        # Save to CSV using DataVisualizer
        self.visualizer.save_to_csv(all_qa_pairs)

        return all_qa_pairs
