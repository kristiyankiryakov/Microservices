#!/usr/bin/env python3

import json
import logging
from pprint import pformat
import sys
import os
from dotenv import load_dotenv
import requests

load_dotenv()


def fetch_playlist_items_page(google_api_key, playlist_id, page_token=None):
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/playlistItems",
        params={
            "key": google_api_key,
            "playlistId": playlist_id,
            "part": "contentDetails",
            "pageToken": page_token,
        },
    )

    payload = json.loads(response.text)
    logging.debug("GOT RESPONSE: %s", payload)

    return payload


def fetch_videos_page(google_api_key, video_id, page_token=None):
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={
            "key": google_api_key,
            "id": video_id,
            "part": "snippet, statistics",
            "pageToken": page_token,
        },
    )

    payload = json.loads(response.text)
    logging.debug("GOT RESPONSE: %s", payload)

    return payload


def fetch_playlist_items(google_api_key, playlist_id, page_token=None):
    payload = fetch_playlist_items_page(google_api_key, playlist_id, page_token)

    yield from payload["items"]

    next_page_token = payload.get("nextPageToken")

    if next_page_token is not None:
        yield from fetch_playlist_items(google_api_key, playlist_id, next_page_token)


def fetch_videos(google_api_key, playlist_id, page_token=None):
    payload = fetch_videos_page(google_api_key, playlist_id, page_token)

    yield from payload["items"]

    next_page_token = payload.get("nextPageToken")

    if next_page_token is not None:
        yield from fetch_videos(google_api_key, playlist_id, next_page_token)


def summarize_video(video):
    return {
        "video_id": video["id"],
        "title": video["snippet"]["title"],
        "views": int(video["statistics"].get("viewCount", 0)),
        "likes": int(video["statistics"].get("likeCount", 0)),
        "comments": int(video["statistics"].get("commentCount", 0)),
    }


def main():
    logging.info("START")

    google_api_key = os.getenv("GOOGLE_API_KEY")
    playlist_id = os.getenv("PLAYLIST_ID")

    for video_item in fetch_playlist_items(google_api_key, playlist_id):
        video_id = video_item["contentDetails"]["videoId"]
        for video in fetch_videos(google_api_key, video_id):
            logging.info("GOT %s", pformat(summarize_video(video)))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())
