# visualizations.py

# Placeholder for visualization functions or data analysis
# Add functions here as needed

# visualization.py

import csv

def save_to_csv(data, filename):
    '''Saves the question-answer pairs to a CSV file.'''
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Question", "Answer"])
        writer.writerows(data)
