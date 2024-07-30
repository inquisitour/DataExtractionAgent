# config.py

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
APIFY_API_TOKEN = os.getenv('APIFY_API_TOKEN')

# Scraping settings
MAX_DEPTH = 2
CACHE_TTL = 600  # 10 minutes
CACHE_MAXSIZE = 100

# URLs to scrape
URLS_TO_SCRAPE = [
    "https://www.healthline.com/health/eye-health/optometrist-vs-ophthalmologist",
    "https://www.healthdirect.gov.au/ophthalmologist",
    "https://www.med.unc.edu/ophth/for-patients/eye-diseases-and-disorders/",
    "https://healthcare.utah.edu/moran/services",
    "https://www.cdc.gov/vision-health/about-eye-disorders/index.html"
]

# Ophthalmology keywords for filtering
OPHTHALMOLOGY_KEYWORDS = [
    'eye', 'vision', 'optometrist', 'ophthalmologist', 'eye health', 'cataract', 'stye',
    'glaucoma', 'astigmatism', 'strabismus', 'short-sightedness', 'long-sightedness',
    'macular degeneration', 'retina', 'cornea', 'lasik', 'myopia', 'hyperopia', 'floaters',
    'dry eye', 'pink eye', 'Amblyopia', 'uveitis', 'keratoconus', 'presbyopia', 'ROP', 'Diabetic retinopathy'
]

# File paths
CSV_OUTPUT_PATH = 'vision_health_qa.csv'
WORDCLOUD_OUTPUT_PATH = 'question_wordcloud.png'
QUESTION_LENGTH_DIST_PATH = 'question_length_distribution.png'
TOP_KEYWORDS_PATH = 'top_keywords.png'

# Visualization settings
WORDCLOUD_WIDTH = 800
WORDCLOUD_HEIGHT = 400
TOP_KEYWORDS_COUNT = 10

# API endpoints
#SCRAPEGRAPHAI_API_URL = "https://api.scrapegraphai.com/scrape"

# Scrapy settings
SCRAPY_SETTINGS = {
    'BOT_NAME': 'ophthalmology',
    'USER_AGENT': 'ophthalmology (Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36)',
    'ROBOTSTXT_OBEY': False,
    'CONCURRENT_REQUESTS': 16,
    'DOWNLOAD_DELAY': 2,
    'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
    'CONCURRENT_REQUESTS_PER_IP': 8,
    'SPIDER_MIDDLEWARES': {
        'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': 50,
        'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 100,
    },
    'DOWNLOADER_MIDDLEWARES': {
        'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 400,
    },
    'EXTENSIONS': {
        'scrapy.extensions.telnet.TelnetConsole': None,
    },
    
    'AUTOTHROTTLE_ENABLED': True,
    'AUTOTHROTTLE_START_DELAY': 5,
    'AUTOTHROTTLE_MAX_DELAY': 60,
    'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
    'AUTOTHROTTLE_DEBUG': False,
    'HTTPCACHE_ENABLED': True,
    'HTTPCACHE_EXPIRATION_SECS': 86400,
    'HTTPCACHE_DIR': 'httpcache',
    'HTTPCACHE_IGNORE_HTTP_CODES': [],
    'HTTPCACHE_STORAGE': 'scrapy.extensions.httpcache.FilesystemCacheStorage',
    'LOG_LEVEL': 'DEBUG'
}

