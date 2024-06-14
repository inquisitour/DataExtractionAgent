import requests
from bs4 import BeautifulSoup
import csv
from requests.exceptions import RequestException
from urllib.parse import urljoin, urlparse

def fetch_page(url):
    '''Fetches the content of a web page given its URL.'''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content
    except RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None

def extract_questions_answers(soup):
    '''Extracts question-answer pairs from a BeautifulSoup object representing a parsed HTML page.'''

    qa_pairs = []
    unique_questions = set()  # To store unique questions

    def add_qa_pair(question, answer):
        ''' Adds a question-answer pair to qa_pairs if the question is unique.
        Args:
        - question (str): The question to add.
        - answer (str): The answer to add.
        '''

        if question not in unique_questions:
            unique_questions.add(question)
            qa_pairs.append((question, answer))


    def find_questions_answers(soup):
        '''Finds questions and answers in the given BeautifulSoup element.
        Args:
        - element (BeautifulSoup): The BeautifulSoup element to search for questions and answers.

        '''
        question_text = None
        answer_text = None

        def add_current_qa_pair():
            '''Adds the current question-answer pair to qa_pairs and resets question_text and answer_text.'''
            nonlocal question_text, answer_text
            if question_text and answer_text:
                if len(answer_text.split()) > 100:
                    answer_text = ' '.join(answer_text.split()[:100]) + '...'
                add_qa_pair(question_text.strip(), answer_text.strip())
                question_text = None
                answer_text = None


        # Iterate through HTML tags to find questions (headers) and answers (paragraphs)
        for tag in soup.find_all(['h1', 'h2', 'h3','p'], recursive=True):
            if tag.name in ['h1', 'h2', 'h3']:
                add_current_qa_pair()
                question_text = tag.get_text(strip=True)
            elif tag.name == 'p':
                if question_text:
                    if answer_text:
                        answer_text += " " + tag.get_text(strip=True)
                    else:
                        answer_text = tag.get_text(strip=True)
        
        add_current_qa_pair()  # Add the last collected pair if any

    find_questions_answers(soup)
    return qa_pairs

def is_valid_ophthalmology_question(question):
    # Add some Keywords related to ophthalmology
    ophthalmology_keywords = ['eye', 'vision', 'optometrist', 'ophthalmologist', 'eye health', 'cataract','glaucoma','astigmatism','Strabismus','short-sightedness','long-sightedness',
    'macular degeneration', 'retina', 'cornea', 'LASIK','myopia', 'hyperopia', 'dry eye', 'uveitis', 'keratoconus', 'presbyopia']
    return any(keyword.lower() in question.lower() for keyword in ophthalmology_keywords)

def save_to_csv(data, filename):
    ''' Saves the question-answer pairs to a CSV file.'''

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Answer"])
        writer.writerows(data)

def crawl(urls, depth=2):
    ''' Crawls a web page and its subpages recursively, extracting ophthalmology-related question-answer pairs.

    Args:
    - url (str): The URL of the starting web page.
    - depth (int): The maximum depth of recursion for crawling subpages.

    '''
    visited_urls = set()
    all_qa_pairs = []
    unique_questions = set()  # To track unique questions

    def recursive_crawl(url, current_depth):
        ''' Recursively crawls the given URL up to the specified depth.   '''
        if url in visited_urls or current_depth > depth:
            return
        visited_urls.add(url)
        
        page_content = fetch_page(url)
        if page_content:
            soup = BeautifulSoup(page_content, 'html.parser')
            qa_pairs = extract_questions_answers(soup)
            
            # Filter and add only unique ophthalmology-related QA pairs
            for q, a in qa_pairs:
                if is_valid_ophthalmology_question(q) and q.endswith('?') and q not in unique_questions:
                    unique_questions.add(q)
                    all_qa_pairs.append((q, a))

            # Find links in the current page and recursively crawl them
            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                if urlparse(next_url).scheme in ['http', 'https']:  # Crawl both HTTP and HTTPS links
                    recursive_crawl(next_url, current_depth + 1)
    for url in urls:
        recursive_crawl(url, 0)
    return all_qa_pairs

def main():
    ''' Main function to initiate crawling and save the data to a CSV file.
        Add new url to extract data '''
    start_urls = [
                "https://www.healthline.com/health/eye-health/optometrist-vs-ophthalmologist",
                "https://www.healthdirect.gov.au/ophthalmologist",
                "https://www.webmd.com/eye-health/default.htm"
                ]

    all_qa_pairs = crawl(start_urls)

    save_to_csv(all_qa_pairs, "vision_health_qa.csv")
    print("Data extraction and saving completed.")

if __name__ == "__main__":
    main()
