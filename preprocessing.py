# preprocessing.py

import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import config

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

class Preprocessor:
    def __init__(self):
        self.unwanted_phrases = [
            "DownloadPDF", "Copy", "Click here", "Read more"
        ]
        self.irrelevant_phrases = [
            "About Us", "Academics", "Research", "Billing", "Find an Interpreter", "Giving","healthdirect Australia free service talk nurse doctor help know",
            "Jobs", "Maps & Directions", "Newsroom", "Referring Providers", "Patient Rights & Responsibilities",
            "Disclaimer", "Privacy Statement", "Public Information Policy", "Non-Discrimination Policy","call triple zero immediately",
            "Surprise Billing Rights", "Webmaster", "65 Mario Capecchi Drive", "Salt Lake City", "Utah", "801-581-2352","need urgent medical help",
            "Last medically reviewed", "Retrieved from", "Our experts continually monitor", "Medically reviewed by" ,"Medical problem ? Call",
        ]
        self.stop_words = set(stopwords.words('english'))
        self.ophthalmology_keywords = config.OPHTHALMOLOGY_KEYWORDS

    def clean_text(self, text):
        '''Clean text by removing unwanted patterns and ensuring proper spacing.'''
        text = re.sub(r'http\S+|www.\S+', '', text)  # Remove URLs
        text = re.sub(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', '', text)  # Remove dates
        text = re.sub(r'\b\d{10}\b', '', text)  # Remove phone numbers
        text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '', text)  # Remove phone numbers
        text = re.sub(r'\b\d{1,5}\s\w+\s\w+\b', '', text)  # Remove addresses

        for phrase in self.unwanted_phrases + self.irrelevant_phrases:
            text = text.replace(phrase, "")

        text = re.sub(r'\s+', ' ', text).strip()

        word_tokens = word_tokenize(text)
        text = ' '.join([word for word in word_tokens if word.lower() not in self.stop_words])

        return text

    def truncate_answer(self, answer):
        '''Truncate answer to a maximum number of words for uniformity.'''
        words = answer.split()
        truncated_answer = ' '.join(words[:300])
        if not truncated_answer.endswith('.'):
            truncated_answer += '.'
        return truncated_answer

    def filter_irrelevant_sentences(self, text):
        '''Filter out irrelevant sentences from the text.'''
        sentences = text.split('. ')
        relevant_sentences = [sentence for sentence in sentences if not any(phrase in sentence for phrase in self.irrelevant_phrases)]
        return '. '.join(relevant_sentences)

    def contains_keywords(self, text):
        '''Checks if the text contains any ophthalmology-related keywords.'''
        if not text:
            return False
        text = text.lower()  # Convert text to lowercase for case-insensitive matching
        return any(keyword.lower() in text for keyword in self.ophthalmology_keywords)

    def validate_answer(self, answer):
        '''Validates if the answer is of appropriate length and relevance.'''
        return 10 <= len(answer.split()) <= 300  # Example criteria: length between 10 and 300 words

    def is_perfect_pair(self, question, answer):
        '''Check if a question-answer pair is perfect and does not need further processing.'''
        return (self.contains_keywords(question) and self.validate_answer(answer)
                and self.clean_text(question) == question
                and self.clean_text(answer) == answer)

    def preprocess_qa_pair(self, question, answer):
        '''Preprocess a question-answer pair if needed.'''
        if self.is_perfect_pair(question, answer):
            # If the QA pair is perfect, return as is
            return question, answer

        if not self.contains_keywords(question):
            return None, None  # Skip questions not related to ophthalmology
        if not self.validate_answer(answer):
            return None, None  # Skip invalid answers

        # Clean and filter if necessary
        cleaned_question = self.clean_text(question)
        cleaned_answer = self.clean_text(answer)
        filtered_answer = self.filter_irrelevant_sentences(cleaned_answer)
        truncated_answer = self.truncate_answer(filtered_answer)

        return cleaned_question, truncated_answer

    def preprocess_data(self, qa_pairs):
        '''Process raw QA pairs and return a list of processed pairs.'''
        processed_pairs = []
        for question, answer in qa_pairs:
            if self.is_perfect_pair(question, answer):
                # If the QA pair is perfect, no further processing is needed
                processed_pairs.append((question, answer))
                continue

            if not self.contains_keywords(question):
                # Skip questions not related to ophthalmology
                continue
            if not self.validate_answer(answer):
                # Skip invalid answers
                continue

            # Clean and truncate if necessary
            cleaned_question = self.clean_text(question)
            cleaned_answer = self.clean_text(answer)
            filtered_answer = self.filter_irrelevant_sentences(cleaned_answer)
            truncated_answer = self.truncate_answer(filtered_answer)

            processed_pairs.append((cleaned_question, truncated_answer))

        return processed_pairs