# DataExtraction.py


import csv
import logging
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from cachetools import TTLCache
from preprocessing import Preprocessor
from visualization import DataVisualizer
import config

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
        self.preprocessor = Preprocessor()
        self.visualizer = DataVisualizer()  # Initialize DataVisualizer

    def parse_item(self, response):
        try:
            logger.info(f"Scraping URL: {response.url}")

            # Extract questions and answers
            questions = response.css('h1::text, h2::text, h3::text, div a::text').getall()
            p_answers = response.css('p::text').getall()
            li_answers = response.css('li::text').getall()
            combined_answers = p_answers + li_answers

            # Filter questions and answers
            filtered_questions = [q for q in questions if q.strip().endswith('?')]
            filtered_answers = [a for a in combined_answers if a.strip()]

            logger.info(f"Found {len(filtered_questions)} questions and {len(filtered_answers)} answers")

            # Preprocess and prepare data for saving
            processed_data = []
            for q, a in zip(filtered_questions, filtered_answers):
                cleaned_question, processed_answer = self.preprocessor.preprocess_qa_pair(q, a)
                if cleaned_question and processed_answer:
                    processed_data.append({'question': cleaned_question, 'answer': processed_answer})

            logger.info(f"Processed Data: {processed_data}")

            if processed_data:
                # Save data to CSV using DataVisualizer
                self.visualizer.save_to_csv(processed_data)
            else:
                logger.warning("No processed data to save.")
        except Exception as e:
            logger.error(f"Error in parse_item: {e}")

class ScrapingManager:
    def __init__(self):
        self.cache = TTLCache(maxsize=config.CACHE_MAXSIZE, ttl=config.CACHE_TTL)
        self.preprocessor = Preprocessor()
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        
        # Initialize CrawlerProcess with settings from config
        self.crawl_process = CrawlerProcess(settings=config.SCRAPY_SETTINGS)
        
    async def scrape_data(self, urls, depth=config.MAX_DEPTH):
        all_qa_pairs = []

        # Check cache first
        cached_results = [self.cache.get(url) for url in urls if url in self.cache]
        if cached_results:
            all_qa_pairs.extend([item for sublist in cached_results for item in sublist])
            urls = [url for url in urls if url not in self.cache]

        if urls:
            # Start the Scrapy crawl
            self.crawl_process.crawl(OphthalmologySpider, start_urls=urls)
            
            # Wait until the crawl is finished
            self.crawl_process.start(stop_after_crawl=True)
            
            # Update cache
            for url in urls:
                self.cache[url] = all_qa_pairs

        return all_qa_pairs
