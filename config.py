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
    "https://www.webmd.com/eye-health/default.htm",
    "https://www.aao.org/eye-health",
    "https://www.med.unc.edu/ophth/for-patients/eye-diseases-and-disorders/",
    "https://healthcare.utah.edu/moran/services",
    "https://www.cdc.gov/vision-health/about-eye-disorders/index.html",
    "https://medlineplus.gov/eyesandvision.html",
    "https://www.news-medical.net/condition/Eye-Health"
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
SCRAPEGRAPHAI_API_URL = "https://api.scrapegraphai.com/scrape"