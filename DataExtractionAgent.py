import aiohttp
import asyncio
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin, urlparse
import time
import nest_asyncio

# Apply nest_asyncio to allow nested use of asyncio
nest_asyncio.apply()

async def fetch_page(session, url):
    '''Fetches the content of a web page given its URL using aiohttp.'''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        print(f"Request failed for {url}: {e}")
        return None

def extract_questions_answers(soup):
    '''Extracts question-answer pairs from a BeautifulSoup object representing a parsed HTML page.'''
    qa_pairs = []
    question_text = None
    answer_text = None

    for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'strong', 'b'], recursive=True):
        text = tag.get_text(strip=True)
        if tag.name in ['h1', 'h2', 'h3', 'strong', 'b'] and text.endswith('?'):
            if question_text and answer_text:
                qa_pairs.append((question_text, answer_text.strip()))
            question_text = text
            answer_text = ''
        elif question_text:
            if tag.name in ['p', 'li']:
                if answer_text:
                    answer_text += ' ' + text
                else:
                    answer_text = text

                # Limit answer to 200 words
                if len(answer_text.split()) > 200:
                    answer_text = ' '.join(answer_text.split()[:200]) + '.'
                    break  # Stop adding more content to the current answer

            elif not question_text.endswith('?'):
                qa_pairs.append((question_text, text.strip()))
                question_text = None

    if question_text and answer_text:
        qa_pairs.append((question_text, answer_text.strip()))

    return qa_pairs

def is_valid_ophthalmology_question(question):
    '''Checks if a question is related to ophthalmology.'''
    ophthalmology_keywords = [
        'eye', 'vision', 'optometrist', 'ophthalmologist', 'eye health', 'cataract', 'stye',
        'glaucoma', 'astigmatism', 'strabismus', 'short-sightedness', 'long-sightedness',
        'macular degeneration', 'retina', 'cornea', 'lasik', 'myopia', 'hyperopia', 'floaters',
        'dry eye', 'pink eye', 'Amblyopia', 'uveitis', 'keratoconus', 'presbyopia', 'ROP', 'Diabetic retinopathy'
    ]
    return any(keyword.lower() in question.lower() for keyword in ophthalmology_keywords)

def save_to_csv(data, filename):
    '''Saves the question-answer pairs to a CSV file.'''
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Answer"])
        writer.writerows(data)

async def process_url(url, session, visited_urls, depth, seen_qa_pairs):
    '''Processes a single URL to extract question-answer pairs and recursively processes subpages.'''
    if url in visited_urls or depth == 0:
        return []

    visited_urls.add(url)
    qa_pairs = []

    page_content = await fetch_page(session, url)
    if page_content:
        soup = BeautifulSoup(page_content, 'html.parser')
        extracted_pairs = extract_questions_answers(soup)
        for q, a in extracted_pairs:
            if is_valid_ophthalmology_question(q) and (q, a) not in seen_qa_pairs:
                seen_qa_pairs.add((q, a))
                qa_pairs.append((q, a))

        # Recursively process subpages
        tasks = []
        for link in soup.find_all('a', href=True):
            next_url = urljoin(url, link['href'])
            if urlparse(next_url).scheme in ['http', 'https']:  # Crawl both HTTP and HTTPS links
                tasks.append(process_url(next_url, session, visited_urls, depth - 1, seen_qa_pairs))
        subpage_qa_pairs = await asyncio.gather(*tasks)
        for pairs in subpage_qa_pairs:
            qa_pairs.extend(pairs)

    return qa_pairs

async def crawl(urls, depth=2):
    '''Processes each URL to extract ophthalmology-related question-answer pairs.'''
    all_qa_pairs = []
    visited_urls = set()
    seen_qa_pairs = set()

    async with aiohttp.ClientSession() as session:
        for url in urls:
            qa_pairs = await process_url(url, session, visited_urls, depth, seen_qa_pairs)
            all_qa_pairs.extend(qa_pairs)

    return all_qa_pairs

def main():
    '''Main function to initiate crawling and save the data to a CSV file.'''
    start_urls = [
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

    start_time = time.time()

    # Run the async crawl function
    all_qa_pairs = asyncio.run(crawl(start_urls))

    end_time = time.time()

    save_to_csv(all_qa_pairs, "vision_health_qa.csv")
    print(f"Data extraction and saving completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
