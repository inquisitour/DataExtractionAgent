# Agent.py

import asyncio
import threading
import time
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import httpx
from extraction import ScrapingManager
from visualization import DataVisualizer
import config

app = FastAPI()

class ScrapeRequest(BaseModel):
    urls: list[str] = None
    depth: int = None
    webhook_url: str = None

scraping_manager = ScrapingManager()
data_visualizer = DataVisualizer()

@app.post("/scrape")
async def scrape(request: ScrapeRequest):
    urls = request.urls if request.urls else config.URLS_TO_SCRAPE
    depth = request.depth if request.depth else config.MAX_DEPTH
    
    try:
        # Start scraping and preprocessing
        qa_pairs = await scraping_manager.scrape_data(urls, depth)
        data_visualizer.visualize_data(qa_pairs)
        
        # Shutdown server after completing tasks
        loop = asyncio.get_event_loop()
        loop.stop()
        
        return {"message": "Scraping completed", "qa_pairs_count": len(qa_pairs)}
    except Exception as e:
        return {"error": f"An error occurred during scraping: {e}"}

# Uncomment the webhook scraping endpoint if needed
# @app.post("/scrape-webhook")
# async def scrape_webhook(request: ScrapeRequest, background_tasks: BackgroundTasks):
#     if not request.webhook_url:
#         return {"error": "Webhook URL is required for this endpoint"}
    
#     urls = request.urls if request.urls else config.URLS_TO_SCRAPE
#     depth = request.depth if request.depth else config.MAX_DEPTH
    
#     background_tasks.add_task(scraping_manager.scrape_data_with_webhook, urls, depth, request.webhook_url)
    
#     return {"message": "Scraping task initiated. Results will be sent to the provided webhook."}

async def send_post_request_to_scrape():
    url = "http://127.0.0.1:8000/scrape"
    payload = {
        "urls": config.URLS_TO_SCRAPE,
        "depth": config.MAX_DEPTH
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        print(response.json())

# Uncomment if you need to test webhook endpoint
# async def send_post_request_to_scrape_webhook():
#     url = "http://127.0.0.1:8000/scrape-webhook"
#     payload = {
#         "urls": config.URLS_TO_SCRAPE,
#         "depth": config.MAX_DEPTH,
#         "webhook_url": "http://your-webhook-url"  # Replace with your actual webhook URL
#     }
#     async with httpx.AsyncClient() as client:
#         response = await client.post(url, json=payload)
#         print(response.json())

if __name__ == "__main__":
    def run_server():
        uvicorn.run(app, host="0.0.0.0", port=8000)

    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # Give the server a moment to start
    time.sleep(2)

    # Send POST requests
    asyncio.run(send_post_request_to_scrape())
    # asyncio.run(send_post_request_to_scrape_webhook())

    # Wait for the server thread to complete
    server_thread.join()
