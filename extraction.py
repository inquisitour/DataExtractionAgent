# DataExtraction.py

import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from scrapy.crawler import CrawlerProcess
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from apify_client import ApifyClient
from cachetools import TTLCache
from preprocessing import Preprocessor
import config

class OphthalmologySpider(CrawlSpider):
    name = 'ophthalmology'
    allowed_domains = list(set([urlparse(url).netloc for url in config.URLS_TO_SCRAPE]))
    start_urls = config.URLS_TO_SCRAPE

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        preprocessor = Preprocessor()
        questions = response.css('h2::text').getall()
        answers = response.css('p::text').getall()
        for q, a in zip(questions, answers):
            yield {
                'question': preprocessor.clean_text(q),
                'answer': preprocessor.preprocess_answer(a)
            }

class ScrapingManager:
    def __init__(self):
        self.cache = TTLCache(maxsize=config.CACHE_MAXSIZE, ttl=config.CACHE_TTL)
        self.preprocessor = Preprocessor()
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

    async def scrape_with_scrapegraphai(self, url):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.OPENAI_API_KEY}"
        }
        payload = {"url": url, "target": "ophthalmology_qa_pairs"}

        async with httpx.AsyncClient() as client:
            response = await client.post(config.SCRAPEGRAPHAI_API_URL, json=payload, headers=headers)
            return response.json()

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
        run = client.actor("apify/web-scraper").call(run_input=run_input)
        return client.dataset(run["defaultDatasetId"]).list_items().items

    async def scrape_data(self, urls, depth=config.MAX_DEPTH):
        all_qa_pairs = []

        # Check cache first
        cached_results = [self.cache.get(url) for url in urls if url in self.cache]
        if cached_results:
            all_qa_pairs.extend([item for sublist in cached_results for item in sublist])
            urls = [url for url in urls if url not in self.cache]

        if urls:
            # ScrapeGraphAI
            scrapegraphai_results = await asyncio.gather(*[self.scrape_with_scrapegraphai(url) for url in urls])
            all_qa_pairs.extend([item for sublist in scrapegraphai_results for item in sublist])

            # Scrapy
            process = CrawlerProcess(settings={
                'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            })
            process.crawl(OphthalmologySpider, start_urls=urls)
            process.start()

            # Apify
            apify_results = self.scrape_with_apify(urls)
            all_qa_pairs.extend(apify_results)

            # Update cache
            for url, result in zip(urls, scrapegraphai_results):
                self.cache[url] = result

        return all_qa_pairs

    async def scrape_data_with_webhook(self, urls, depth, webhook_url):
        qa_pairs = await self.scrape_data(urls, depth)
        # Send results to webhook
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json={"qa_pairs": qa_pairs})