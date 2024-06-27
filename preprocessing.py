# preprocessing.py

import re
import requests

def clean_text(text):
    '''Clean text by removing unwanted patterns and ensuring proper spacing.'''
    unwanted_phrases = ["DownloadPDF", "Copy", "Click here", "Read more"]
    irrelevant_phrases = [
        "About Us", "Academics", "Research", "Billing", "Find an Interpreter", "Giving",
        "Jobs", "Maps & Directions", "Newsroom", "Referring Providers", "Patient Rights & Responsibilities",
        "Disclaimer", "Privacy Statement", "Public Information Policy", "Non-Discrimination Policy",
        "Surprise Billing Rights", "Webmaster", "65 Mario Capecchi Drive", "Salt Lake City", "Utah", "801-581-2352",
        "Last medically reviewed", "Retrieved from", "Our experts continually monitor", "Medically reviewed by"
    ]

    # Remove unwanted patterns
    text = re.sub(r'http\S+|www.\S+', '', text)  # Remove URLs
    text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '', text)  # Remove dates
    text = re.sub(r'\b\d{10}\b', '', text)  # Remove phone numbers (simple regex for 10-digit numbers)
    text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '', text)  # Remove phone numbers (formatted as 123-456-7890)
    text = re.sub(r'\b\d{1,5}\s\w+\s\w+\b', '', text)  # Remove simple addresses

    # Remove unwanted and irrelevant phrases
    for phrase in unwanted_phrases + irrelevant_phrases:
        text = text.replace(phrase, "")

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def truncate_answer(answer):
    '''Truncate answer to a maximum number of words for uniformity.'''
    words = answer.split()
    truncated_answer = ' '.join(words[:300])  # Limiting the answer to 300 words for uniformity
    if not truncated_answer.endswith('.'):
        truncated_answer += '.'
    return truncated_answer

def call_scrapegraphai_api(text):
    '''Call ScrapeGraphAI API to clean and preprocess the text.'''
    api_url = "https://api.scrapegraphai.com/preprocess"  # Replace with actual ScrapeGraphAI endpoint
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY"  # Add your API key if required
    }
    payload = {"text": text}

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get('cleaned_text', text)
    except requests.exceptions.RequestException as e:
        print(f"Error calling ScrapeGraphAI API: {e}")
        return text  # Return original text if API call fails

def filter_irrelevant_sentences(text):
    '''Filter out irrelevant sentences from the text.'''
    irrelevant_phrases = [
        "Last medically reviewed", "Retrieved from", "Our experts continually monitor", "Medically reviewed by",
        "Google Gemini", "Bard", "board examination", "Screen time significantly associated with"
    ]
    sentences = text.split('. ')
    relevant_sentences = [sentence for sentence in sentences if not any(phrase in sentence for phrase in irrelevant_phrases)]
    return '. '.join(relevant_sentences)
