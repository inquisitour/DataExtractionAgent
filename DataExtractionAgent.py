import requests
from bs4 import BeautifulSoup
import csv
from requests.exceptions import RequestException
from urllib.parse import urljoin, urlparse

def fetch_page(url):
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
    '''Checks if a question is valid for ophthalmology-related content.
        Args:
    - soup (BeautifulSoup): The BeautifulSoup object representing the parsed HTML content of a web page.

    '''

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


    def find_questions_answers(element):
        '''Finds questions and answers in the given BeautifulSoup element.
        Args:
        - element (BeautifulSoup): The BeautifulSoup element to search for questions and answers.

        '''
        question_text = ''
        answer_text = ''
        for tag in element.find_all(['h1', 'h2', 'h3', 'p'], recursive=True):  # Search for questions in multiple tags
            if tag.name in ['h1', 'h2', 'h3'] and tag.get_text(strip=True).endswith('?') and len(tag.get_text(strip=True).split()) <= 15:  # Adjust the maximum number of words here
                # Store the previous question-answer pair if found
                if question_text and answer_text:
                    add_qa_pair(question_text.strip(), answer_text.strip())
                    question_text = ''
                    answer_text = ''
                
                question_text = tag.get_text(strip=True)
            elif tag.name == 'p' and question_text:  # Capture answer only if there's a preceding question
                answer_text = tag.get_text(strip=True)
                if answer_text:  # Limit the answer to 100 words if it's too long
                    words = answer_text.split()
                    if len(words) > 100:
                        answer_text = ' '.join(words[:100]) + '...'

                add_qa_pair(question_text.strip(), answer_text.strip())
                question_text = ''  # Reset question_text for the next question

        # Append the last question-answer pair found
        if question_text and answer_text:
            add_qa_pair(question_text.strip(), answer_text.strip())

    find_questions_answers(soup)
    return qa_pairs

def is_valid_ophthalmology_question(question):
    # Add validation logic here. For simplicity, we check for keywords related to ophthalmology
    ophthalmology_keywords = ['eye', 'vision', 'optometrist', 'ophthalmologist', 'eye health', 'cataract','glaucoma','astigmatism','Strabismus','short-sightedness','long-sightedness']
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
                if is_valid_ophthalmology_question(q) and q not in unique_questions:
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
    '''    Main function to initiate crawling and save the data to a CSV file. '''
    start_urls = [
                "https://www.healthline.com/health/eye-health/optometrist-vs-ophthalmologist",
                "https://www.healthdirect.gov.au/ophthalmologist" 
                ]

    all_qa_pairs = crawl(start_urls)

    save_to_csv(all_qa_pairs, "vision_health_qa.csv")
    print("Data extraction and saving completed.")

if __name__ == "__main__":
    main()
