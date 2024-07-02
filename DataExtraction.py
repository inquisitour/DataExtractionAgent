# extraction.py

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from preprocessing import clean_text, truncate_answer, filter_irrelevant_sentences, call_scrapegraphai_api

# Define the keywords for filtering ophthalmology-related questions
ophthalmology_keywords = [
    'eye', 'vision', 'optometrist', 'ophthalmologist', 'eye health', 'cataract', 'stye',
    'glaucoma', 'astigmatism', 'strabismus', 'short-sightedness', 'long-sightedness',
    'macular degeneration', 'retina', 'cornea', 'lasik', 'myopia', 'hyperopia', 'floaters',
    'dry eye', 'pink eye', 'Amblyopia', 'uveitis', 'keratoconus', 'presbyopia', 'ROP', 'Diabetic retinopathy'
]

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
    answer_text = []

    for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'strong', 'b'], recursive=True):
        text = clean_text(tag.get_text(strip=True))

        if tag.name in ['h1', 'h2', 'h3', 'strong', 'b'] and text.endswith('?'):
            if question_text and answer_text:
                answer = ' '.join(answer_text).strip()
                answer = filter_irrelevant_sentences(answer)
                clean_answer = call_scrapegraphai_api(truncate_answer(answer))
                qa_pairs.append((question_text, clean_answer))
            question_text = text
            answer_text = []
        elif question_text:
            if tag.name in ['p', 'li'] and not text.endswith('?'):  # Ensure that the answer part does not contain questions
                answer_text.append(text)
                # Truncate answer to maximum words
                if len(' '.join(answer_text).split()) > 300:
                    answer_text = answer_text[:300]
                    break  # Stop adding more content to the current answer

    if question_text and answer_text:
        answer = ' '.join(answer_text).strip()
        answer = filter_irrelevant_sentences(answer)
        clean_answer = call_scrapegraphai_api(truncate_answer(answer))
        qa_pairs.append((question_text, clean_answer))

    return qa_pairs

def is_valid_ophthalmology_question(question):
    '''Checks if a question is related to ophthalmology.'''
    return any(keyword.lower() in question.lower() for keyword in ophthalmology_keywords)

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
            if is_valid_ophthalmology_question(q):
                qa_pair = (q, a)
                if qa_pair not in seen_qa_pairs:
                    seen_qa_pairs.add(qa_pair)
                    qa_pairs.append(qa_pair)

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

    # Sort and deduplicate to ensure consistency
    all_qa_pairs = sorted(set(all_qa_pairs), key=lambda x: (x[0], x[1]))
    return all_qa_pairs
