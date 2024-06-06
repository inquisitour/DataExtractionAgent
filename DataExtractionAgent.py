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

def parse_questions_answers(soup):
    qa_pairs = []
    # Adjusting to extract <h1> tags as questions and their subsequent <p> tags as answers
    questions = soup.find_all('h1')
    for question in questions:
        answer = question.find_next('p')
        question_text = question.get_text(strip=True)
        answer_text = answer.get_text(strip=True) if answer else 'No answer found'
        if is_valid_ophthalmology_question(question_text):
            qa_pairs.append((question_text, answer_text))
    return qa_pairs

def is_valid_ophthalmology_question(question):
    # Add validation logic here. For simplicity, we check for keywords related to ophthalmology
    ophthalmology_keywords = ['eye', 'vision', 'optometrist', 'ophthalmologist', 'eye health']
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
            qa_pairs = parse_questions_answers(soup)
            all_qa_pairs.extend(qa_pairs)
    
    save_to_csv(all_qa_pairs, "vision_health_qa.csv")
    print("Data extraction and saving completed.")

if __name__ == "__main__":
    main()
