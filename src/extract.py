import os
import sys
from pathlib import Path
import logging
import json
from datetime import datetime
from typing import Optional
from googleapiclient.discovery import build
from dotenv import dotenv_values


config = dotenv_values("../.env")
API_KEY = config["API_KEY"]
REGION_CODES_FILE = Path("../data/input/region_codes.txt")
STAGING_DIR = "../data/staging/"
LOG_FILE = Path(STAGING_DIR) / "etl.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)


def region_codes() -> list[str]:
    try:
        with open(REGION_CODES_FILE, "r", encoding="utf-8") as codes:
            REGION_CODES = [code.rstrip("\n") for code in codes]
        return REGION_CODES
    except FileNotFoundError:
        logging.error(
            "Please make sure the region_codes.txt file exists in the provided path!"
        )
        sys.exit(1)


def fetch_trending_videos(region_code: str, next_page_token: Optional[str]) -> dict:
    try:
        youtube = build("youtube", "v3", developerKey=API_KEY)
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics,topicDetails,status,recordingDetails,player",
            fields="items(id, contentDetails(caption, duration), "
            "statistics(commentCount, likeCount, viewCount), "
            "snippet(channelId, channelTitle, title, categoryId, tags, publishedAt, description)), "
            "nextPageToken",
            chart="mostPopular",
            regionCode=region_code,
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request.execute()
        return dict(response)
    except Exception as e:
        logging.error(f"Failed to fetch data for {region_code}:\n {str(e)}")
        return {}
