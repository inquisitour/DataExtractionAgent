# Agent.py

import asyncio
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
from extraction import ScrapingManager
from visualization import DataVisualizer
import nest_asyncio
import config

# Apply nest_asyncio to allow nested use of asyncio
nest_asyncio.apply()

app = FastAPI()

class ScrapeRequest(BaseModel):
    urls: list[str] = config.URLS_TO_SCRAPE
    depth: int = config.MAX_DEPTH
    webhook_url: str = None

scraping_manager = ScrapingManager()
data_visualizer = DataVisualizer()

@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    qa_pairs = await scraping_manager.scrape_data(request.urls, request.depth)
    data_visualizer.visualize_data(qa_pairs)
    return {"message": "Scraping completed", "qa_pairs_count": len(qa_pairs)}

@app.post("/scrape-webhook")
async def scrape_webhook(request: ScrapeRequest, background_tasks: BackgroundTasks):
    if not request.webhook_url:
        return {"error": "Webhook URL is required for this endpoint"}
    
    background_tasks.add_task(scraping_manager.scrape_data_with_webhook, request.urls, request.depth, request.webhook_url)
    return {"message": "Scraping task initiated. Results will be sent to the provided webhook."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
