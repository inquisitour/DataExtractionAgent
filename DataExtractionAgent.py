import requests
from bs4 import BeautifulSoup
import csv
from requests.exceptions import RequestException

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
    qa_pairs = []
    unique_questions = set()  # To store unique questions

    def add_qa_pair(question, answer):
        if question not in unique_questions:
            unique_questions.add(question)
            qa_pairs.append((question, answer))

    def find_questions_answers(element):
        for tag in element.find_all(True):  # True means all tags
            question_text = tag.get_text(strip=True)
            if question_text.endswith('?'):
                answer_text = ''
                answer_tag = tag.find_next('p')
                if answer_tag:
                    answer_text = answer_tag.get_text(strip=True)

                # Limit the answer to 100 words
                if answer_text:
                    words = answer_text.split()
                    if len(words) > 100:
                        answer_text = ' '.join(words[:100]) + '...'

                add_qa_pair(question_text, answer_text.strip())

    find_questions_answers(soup)
    return qa_pairs

def is_valid_ophthalmology_question(question):
    # Add validation logic here. For simplicity, we check for keywords related to ophthalmology
    ophthalmology_keywords = ['eye', 'vision', 'optometrist', 'ophthalmologist', 'eye health', 'cataract']
    return any(keyword.lower() in question.lower() for keyword in ophthalmology_keywords)

def save_to_csv(data, filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Answer"])
        writer.writerows(data)

def main():
    urls = [
        "https://www.healthline.com/health/eye-health/optometrist-vs-ophthalmologist#ophthalmologist",
        # Add more URLs here
    ]

    all_qa_pairs = []

    for url in urls:
        page_content = fetch_page(url)
        if page_content:
            soup = BeautifulSoup(page_content, 'html.parser')
            qa_pairs = extract_questions_answers(soup)
            all_qa_pairs.extend(qa_pairs)

    save_to_csv(all_qa_pairs, "vision_health_qa.csv")
    print("Data extraction and saving completed.")

if __name__ == "__main__":
    main()