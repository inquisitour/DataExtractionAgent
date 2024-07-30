# preprocessing.py

import re
import httpx
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import config

nltk.download('punkt')
nltk.download('stopwords')

class Preprocessor:
    def __init__(self):
        self.unwanted_phrases = ["DownloadPDF", "Copy", "Click here", "Read more"]
        self.irrelevant_phrases = [
            "About Us", "Academics", "Research", "Billing", "Find an Interpreter", "Giving",
            "Jobs", "Maps & Directions", "Newsroom", "Referring Providers", "Patient Rights & Responsibilities",
            "Disclaimer", "Privacy Statement", "Public Information Policy", "Non-Discrimination Policy",
            "Surprise Billing Rights", "Webmaster", "65 Mario Capecchi Drive", "Salt Lake City", "Utah", "801-581-2352",
            "Last medically reviewed", "Retrieved from", "Our experts continually monitor", "Medically reviewed by"
        ]
        self.stop_words = set(stopwords.words('english'))
        self.ophthalmology_keywords = config.OPHTHALMOLOGY_KEYWORDS

    def clean_text(self, text):
        '''Clean text by removing unwanted patterns and ensuring proper spacing.'''
        # Remove unwanted patterns
        text = re.sub(r'http\S+|www.\S+', '', text)  # Remove URLs
        text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '', text)  # Remove dates
        text = re.sub(r'\b\d{10}\b', '', text)  # Remove phone numbers (simple regex for 10-digit numbers)
        text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '', text)  # Remove phone numbers (formatted as 123-456-7890)
        text = re.sub(r'\b\d{1,5}\s\w+\s\w+\b', '', text)  # Remove simple addresses

        # Remove unwanted and irrelevant phrases
        for phrase in self.unwanted_phrases + self.irrelevant_phrases:
            text = text.replace(phrase, "")

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Remove stopwords
        word_tokens = word_tokenize(text)
        text = ' '.join([word for word in word_tokens if word.lower() not in self.stop_words])

        return text

    def truncate_answer(self, answer):
        '''Truncate answer to a maximum number of words for uniformity.'''
        words = answer.split()
        truncated_answer = ' '.join(words[:300])  # Limiting the answer to 300 words for uniformity
        if not truncated_answer.endswith('.'):
            truncated_answer += '.'
        return truncated_answer

    #async def call_scrapegraphai_api(self, text):
        #'''Call ScrapeGraphAI API to clean and preprocess the text.'''
        #headers = {
            #"Content-Type": "application/json",
            #"Authorization": f"Bearer {config.OPENAI_API_KEY}"
        #}
        #payload = {"text": text}

        #async with httpx.AsyncClient() as client:
            #response = await client.post(config.SCRAPEGRAPHAI_API_URL, json=payload, headers=headers)
            #if response.status_code == 200:
                #return response.json().get('cleaned_text', text)
            #else:
               # print(f"Error calling ScrapeGraphAI API: {response.status_code}")
                #return text  # Return original text if API call fails

    def filter_irrelevant_sentences(self, text):
        '''Filter out irrelevant sentences from the text.'''
        sentences = text.split('. ')
        relevant_sentences = [sentence for sentence in sentences if not any(phrase in sentence for phrase in self.irrelevant_phrases)]
        return '. '.join(relevant_sentences)

    def preprocess_qa_pair(self, question, answer):
        '''Preprocess a question-answer pair.'''
        cleaned_question = self.clean_text(question)
        cleaned_answer = self.clean_text(answer)
        filtered_answer = self.filter_irrelevant_sentences(cleaned_answer)
        truncated_answer = self.truncate_answer(filtered_answer)
        return cleaned_question, truncated_answer

    def preprocess_answer(self, answer):
        '''Preprocess an answer.'''
        cleaned_answer = self.clean_text(answer)
        filtered_answer = self.filter_irrelevant_sentences(cleaned_answer)
        return self.truncate_answer(filtered_answer)