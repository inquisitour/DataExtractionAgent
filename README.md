# DataExtractionAgent

## 🔬 Project Overview

DataExtractionAgent is an advanced web scraping tool designed to extract question-answer pairs related to ophthalmology from various online sources. It combines modern web scraping techniques with natural language processing to create a comprehensive database of ophthalmology-related information.

### 🌟 Key Features

- **Multi-source Scraping**: Leverages ScrapeGraphAI, Scrapy, and Apify for robust data extraction.
- **AI-Powered Text Processing**: Utilizes NLP techniques for cleaning and preprocessing scraped data.
- **Intelligent Caching**: Implements a caching system to optimize performance and reduce redundant scraping.
- **Data Visualization**: Generates visualizations to provide insights into the scraped data.
- **Webhook Support**: Handles long-running scraping tasks through webhook notifications.
- **Configurable Settings**: Easily customizable via a centralized configuration file.

## 🛠 Setup and Installation

### Prerequisites

- Python 3.12+
- pip (Python package manager)
- Virtual environment (recommended)

### Step-by-step Setup

1. **Clone the repository**
   ```
   git clone https://github.com/yourusername/ophthalmologyqa-web-scraper.git
   cd ophthalmologyqa-web-scraper
   ```

2. **Set up a virtual environment**
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install required packages**
   ```
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with the following content:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   APIFY_API_TOKEN=your_apify_api_token_here
   ```
   Replace the placeholders with your actual API keys.

5. **Configure the application**
   Review and modify `config.py` to adjust settings as needed.

## 🚀 Usage

### Running the Scraper

1. Start the FastAPI server:
   ```
   python Agent.py
   ```

2. The server will run on `http://localhost:8000`.

### API Endpoints

- **POST `/scrape`**: For immediate scraping
  - Body: `{"urls": ["url1", "url2"], "depth": 2}`
  - Returns: Scraping completion message and count of Q&A pairs

- **POST `/scrape-webhook`**: For long-running scraping tasks
  - Body: `{"urls": ["url1", "url2"], "depth": 2, "webhook_url": "https://your-webhook-url.com"}`
  - Returns: Task initiation message

### Default URLs

The scraper includes a pre-configured list of ophthalmology-related websites in the `config.py` file, including sources like Healthline, WebMD, and the American Academy of Ophthalmology.

### Viewing Results

After scraping, you'll find:
- CSV file with Q&A pairs: `vision_health_qa.csv`
- Word cloud image: `question_wordcloud.png`
- Question length distribution: `question_length_distribution.png`
- Top keywords chart: `top_keywords.png`

## 🧠 How It Works

1. **Scraping Process**: Utilizes ScrapeGraphAI, Scrapy, and Apify to extract data from multiple sources.
2. **Data Processing**: Cleans and preprocesses extracted text using NLP techniques.
3. **Data Storage and Visualization**: Stores processed Q&A pairs in a CSV file and generates visualizations.

## 📂 Project Structure

- `Agent.py`: Main entry point and API server
- `DataExtraction.py`: Core scraping logic
- `preprocessing.py`: Text cleaning and preprocessing
- `visualization.py`: Data visualization and CSV generation
- `config.py`: Centralized configuration settings

## 🛠 Customization

- Modify `config.py` to adjust scraping settings and output paths.
- Extend `preprocessing.py` for custom text processing rules.
- Enhance `visualization.py` for additional data visualizations.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add YourFeature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 📞 Support

For issues or questions, please file an issue on the GitHub issue tracker.

## 🙏 Acknowledgements

- OpenAI for their GPT model
- Apify for their web scraping platform
- The Scrapy team for their web scraping framework

Happy scraping! 🕷️🔍👁️
