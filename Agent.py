# Agent.py

import asyncio
import nest_asyncio
from DataExtraction import crawl
from visualization import save_to_csv

# Apply nest_asyncio to allow nested use of asyncio
nest_asyncio.apply()

def main():
    '''Main function to initiate crawling and save the data to a CSV file.'''
    urls = [
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

    loop = asyncio.get_event_loop()
    qa_pairs = loop.run_until_complete(crawl(urls, depth=2))

    # Save to CSV
    save_to_csv(qa_pairs, 'vision_health_qa.csv')

if __name__ == "__main__":
    main()
