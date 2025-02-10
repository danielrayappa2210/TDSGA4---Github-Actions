import json
import httpx
from datetime import datetime, UTC
from lxml import html
from typing import List, Dict
import logging

# Configure logging (do this at the beginning of your script)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_imdb() -> List[Dict[str, str]]:
    """Scrape IMDb Top 250 movies."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; IMDbBot/1.0)"}
    try:
        response = httpx.get("https://www.imdb.com/chart/top/", headers=headers, verify=False)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    except httpx.HTTPError as exc:
        logging.error(f"HTTP error: {exc}")  # Log the error
        return [] # Return an empty list or handle the error as needed

    tree = html.fromstring(response.text)
    movies = []

    for item in tree.cssselect(".ipc-metadata-list-summary-item"):
        title = (
            item.cssselect(".ipc-title__text")[0].text_content()
            if item.cssselect(".ipc-title__text")
            else None
        )
        year = (
            item.cssselect(".cli-title-metadata span")[0].text_content()
            if item.cssselect(".cli-title-metadata span")
            else None
        )
        rating = (
            item.cssselect(".ipc-rating-star")[0].text_content()
            if item.cssselect(".ipc-rating-star")
            else None
        )

        if title and year and rating:
            movies.append({"title": title, "year": year, "rating": rating})

    return movies

# Scrape data and save with timestamp
now = datetime.now(UTC)
try:
    movies = scrape_imdb() # Call the scraping function
    with open(f'imdb-top250-{now.strftime("%Y-%m-%d")}.json', "a") as f:
        data = {"timestamp": now.isoformat(), "movies": movies}
        json.dump(data, f) # Directly dump the dictionary
        f.write("\n")
    logging.info("IMDb data scraped and saved successfully.") # Log success
except Exception as e: # Catch any other exceptions
    logging.error(f"An error occurred: {e}")  # Log the error
    exit(1) # Exit with a non-zero code to indicate failure to the workflow.
