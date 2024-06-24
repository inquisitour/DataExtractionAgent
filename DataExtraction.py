# extraction.py

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import nest_asyncio

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

def clean_text(text):
    '''Clean text by removing unwanted patterns and ensuring proper spacing.'''
    unwanted_phrases = ["DownloadPDF", "Copy", "Click here", "Read more"]
    for phrase in unwanted_phrases:
        text = text.replace(phrase, "")
    return ' '.join(text.split())

def truncate_answer(answer):
    '''Truncate answer to a maximum number of words for uniformity.'''
    words = answer.split()
    truncated_answer = ' '.join(words[:300])  # Limiting the answer to 300 words for uniformity
    if not truncated_answer.endswith('.'):
        truncated_answer += '.'
    return truncated_answer

def extract_questions_answers(soup):
    '''Extracts question-answer pairs from a BeautifulSoup object representing a parsed HTML page.'''
    qa_pairs = []
    question_text = None
    answer_text = []

    for tag in soup.find_all(['h1', 'h2', 'h3', 'p', 'li', 'strong', 'b'], recursive=True):
        text = clean_text(tag.get_text(strip=True))

        if tag.name in ['h1', 'h2', 'h3', 'strong', 'b'] and text.endswith('?'):
            if question_text and answer_text:
                qa_pairs.append((question_text, truncate_answer(' '.join(answer_text).strip())))
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
        qa_pairs.append((question_text, truncate_answer(' '.join(answer_text).strip())))

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
