# DataExtraction.py

import asyncio
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from apify_client import ApifyClient
from cachetools import TTLCache
from preprocessing import Preprocessor  # Make sure this is the correct import path
import config


class OphthalmologySpider(CrawlSpider):
    name = 'ophthalmology'
    allowed_domains = list(set([urlparse(url).netloc for url in config.URLS_TO_SCRAPE]))
    start_urls = config.URLS_TO_SCRAPE

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        try:
            preprocessor = Preprocessor()
            # Extract questions and answers
            questions = response.css('h1::text, h2::text, h3::text, div a::text').getall()
            answers = response.css('p::text').getall()

            # Iterate through extracted questions and answers
            for q, a in zip(questions, answers):
                cleaned_question = preprocessor.clean_text(q)
                processed_answer = preprocessor.preprocess_answer(a)

                # Print the raw question and answer to the terminal
                print(f"Question: {cleaned_question}")
                print(f"Answer: {processed_answer}")
                print("-" * 80)  # Separator for readability

                yield {
                    'question': cleaned_question,
                    'answer': processed_answer
                }
        except Exception as e:
            self.logger.error(f"Error in parse_item: {e}")

class ScrapingManager:
    def __init__(self):
        self.cache = TTLCache(maxsize=config.CACHE_MAXSIZE, ttl=config.CACHE_TTL)
        self.preprocessor = Preprocessor()
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

    # async def scrape_with_scrapegraphai(self, url):
    #     headers = {
    #         "Content-Type": "application/json",
    #         "Authorization": f"Bearer {config.OPENAI_API_KEY}"
    #     }
    #     payload = {"url": url, "target": "ophthalmology_qa_pairs"}
    #
    #     try:
    #         async with httpx.AsyncClient() as client:
    #             response = await client.post(config.SCRAPEGRAPHAI_API_URL, json=payload, headers=headers)
    #             response.raise_for_status()  # Raise an exception for HTTP errors
    #             return response.json()
    #     except httpx.HTTPStatusError as e:
    #         print(f"HTTP error occurred during ScrapeGraphAI request: {e}")
    #     except httpx.RequestError as e:
    #         print(f"Request error occurred during ScrapeGraphAI request: {e}")
    #     except Exception as e:
    #         print(f"Unexpected error occurred during ScrapeGraphAI request: {e}")

    def scrape_with_apify(self, urls):
        client = ApifyClient(config.APIFY_API_TOKEN)
        run_input = {
            "startUrls": [{"url": url} for url in urls],
            "pageFunction": """
            async function pageFunction(context) {
                const { $ } = context;
                const qaData = [];
                $('h2').each((index, element) => {
                    const question = $(element).text().trim();
                    const answer = $(element).next('p').text().trim();
                    if (question && answer) {
                        qaData.push({ question, answer });
                    }
                });
                return qaData;
            }
            """
        }
        try:
            run = client.actor("apify/web-scraper").call(run_input=run_input)
            return client.dataset(run["defaultDatasetId"]).list_items().items
        except Exception as e:
            print(f"Error occurred during Apify scraping: {e}")

    async def scrape_data(self, urls, depth=config.MAX_DEPTH):
        all_qa_pairs = []

        try:
            # Check cache first
            cached_results = [self.cache.get(url) for url in urls if url in self.cache]
            if cached_results:
                all_qa_pairs.extend([item for sublist in cached_results for item in sublist])
                urls = [url for url in urls if url not in self.cache]

            if urls:
                # ScrapeGraphAI
                # scrapegraphai_results = await asyncio.gather(*[self.scrape_with_scrapegraphai(url) for url in urls])
                # all_qa_pairs.extend([item for sublist in scrapegraphai_results for item in sublist])

                # Scrapy
                try:
                    process = CrawlerProcess(settings=config.SCRAPY_SETTINGS)
                    process.crawl(OphthalmologySpider)
                    process.start()
                except Exception as e:
                    print(f"Error occurred during Scrapy crawling: {e}")

                # Apify
                apify_results = self.scrape_with_apify(urls)
                all_qa_pairs.extend(apify_results)

                # Update cache
                # for url, result in zip(urls, scrapegraphai_results):
                #     self.cache[url] = result

        except Exception as e:
            print(f"Unexpected error occurred during scraping data: {e}")

        return all_qa_pairs

    # async def scrape_data_with_webhook(self, urls, depth, webhook_url):
    #     try:
    #         qa_pairs = await self.scrape_data(urls, depth)
    #         # Send results to webhook
    #         async with httpx.AsyncClient() as client:
    #             await client.post(webhook_url, json={"qa_pairs": qa_pairs})
    #     except Exception as e:
    #         print(f"Error occurred while sending data to webhook: {e}")
