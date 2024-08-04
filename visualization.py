# visualization.py

import csv
# import matplotlib.pyplot as plt
# from wordcloud import WordCloud
# import pandas as pd
import config

class DataVisualizer:
    def __init__(self):
        self.clear_csv(config.CSV_OUTPUT_PATH)  # Clear the file and write headers initially
        
    def clear_csv(self, filename):
        '''Clears the CSV file by overwriting it with headers only.'''
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Question", "Answer"])  # Writing headers

    def save_to_csv(self, data, filename=config.CSV_OUTPUT_PATH):
        '''Appends the question-answer pairs to a CSV file.'''
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows([(pair['question'], pair['answer']) for pair in data])

    # def generate_word_cloud(self, data, filename=config.WORDCLOUD_OUTPUT_PATH):
    #     '''Generates a word cloud from the questions and saves it as an image.'''
    #     text = ' '.join([pair['question'] for pair in data])  # Join all questions
    #     wordcloud = WordCloud(width=config.WORDCLOUD_WIDTH, height=config.WORDCLOUD_HEIGHT, background_color='white').generate(text)
        
    #     plt.figure(figsize=(10, 5))
    #     plt.imshow(wordcloud, interpolation='bilinear')
    #     plt.axis('off')
    #     plt.tight_layout(pad=0)
    #     plt.savefig(filename)
    #     plt.close()

    # def plot_question_length_distribution(self, data, filename=config.QUESTION_LENGTH_DIST_PATH):
    #     '''Plots the distribution of question lengths and saves it as an image.'''
    #     question_lengths = [len(pair['question'].split()) for pair in data]
        
    #     plt.figure(figsize=(10, 5))
    #     plt.hist(question_lengths, bins=20, edgecolor='black')
    #     plt.title('Distribution of Question Lengths')
    #     plt.xlabel('Number of Words')
    #     plt.ylabel('Frequency')
    #     plt.savefig(filename)
    #     plt.close()

    # def generate_top_keywords(self, data, filename=config.TOP_KEYWORDS_PATH, top_n=config.TOP_KEYWORDS_COUNT):
    #     '''Generates a bar chart of top keywords in questions and saves it as an image.'''
    #     all_words = ' '.join([pair['question'] for pair in data]).lower().split()
    #     word_freq = pd.Series(all_words).value_counts()
    #     top_words = word_freq.head(top_n)
        
    #     plt.figure(figsize=(10, 5))
    #     top_words.plot(kind='bar')
    #     plt.title(f'Top {top_n} Keywords in Questions')
    #     plt.xlabel('Keywords')
    #     plt.ylabel('Frequency')
    #     plt.tight_layout()
    #     plt.savefig(filename)
    #     plt.close()

    def visualize_data(self, data):
        '''Generates all visualizations for the scraped data.'''
        self.save_to_csv(data)
        # self.generate_word_cloud(data)
        # self.plot_question_length_distribution(data)
        # self.generate_top_keywords(data)
