import requests
import time
import re
from collections import Counter, defaultdict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

# -------------------------------
# YOUTUBE COMPETITOR ANALYZER
# -------------------------------

def get_channel_id_from_handle(api_key, handle):
    handle = handle.replace('@', '')
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': handle,
        'type': 'channel',
        'key': api_key,
        'maxResults': 1
    }
    response = requests.get(url, params=params, timeout=30)
    data = response.json()
    if 'items' in data and data['items']:
        return data['items'][0]['snippet']['channelId']
    return None


def get_channel_stats(api_key, channel_id):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        'part': 'statistics,snippet,contentDetails',
        'id': channel_id,
        'key': api_key
    }
    response = requests.get(url, params=params, timeout=30)
    data = response.json()
    if 'items' in data and data['items']:
        return data['items'][0]
    return None


def get_channel_videos(api_key, channel_id, max_results=15):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        'part': 'contentDetails',
        'id': channel_id,
        'key': api_key
    }
    response = requests.get(url, params=params, timeout=30)
    data = response.json()
    if not data.get('items'):
        return []

    uploads_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params = {
        'part': 'contentDetails',
        'playlistId': uploads_id,
        'maxResults': max_results,
        'key': api_key
    }
    response = requests.get(url, params=params, timeout=30)
    data = response.json()

    video_ids = [item['contentDetails']['videoId'] for item in data.get('items', [])]
    if not video_ids:
        return []

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        'part': 'snippet,statistics,contentDetails',
        'id': ','.join(video_ids),
        'key': api_key
    }
    response = requests.get(url, params=params, timeout=30)
    return response.json().get('items', [])


def parse_channel(channel_data, videos):
    stats = channel_data['statistics']
    snippet = channel_data['snippet']

    subscribers = int(stats.get('subscriberCount', 0))
    if subscribers == 0:
        return None

    total_views = total_likes = total_comments = 0
    parsed_videos = []

    for video in videos:
        v_stats = video['statistics']
        v_snip = video['snippet']

        views = int(v_stats.get('viewCount', 0))
        likes = int(v_stats.get('likeCount', 0))
        comments = int(v_stats.get('commentCount', 0))

        total_views += views
        total_likes += likes
        total_comments += comments

        parsed_videos.append({
            "title": v_snip.get("title", ""),
            "views": views,
            "likes": likes,
            "comments": comments
        })

    count = len(parsed_videos)
    avg_views = total_views // count if count else 0
    avg_likes = total_likes // count if count else 0
    avg_comments = total_comments // count if count else 0
    engagement = round(((avg_likes + avg_comments) / avg_views) * 100, 2) if avg_views else 0

    return {
        "channel_name": snippet.get("title", ""),
        "subscribers": subscribers,
        "avg_views": avg_views,
        "avg_likes": avg_likes,
        "engagement": engagement,
        "videos": parsed_videos
    }


def get_competitor_handles(_):
    return [
        "@MrBeast", "@MKBHD", "@LinusTechTips",
        "@MrWhosetheboss", "@TechnicalGuruji",
        "@TrakinTech", "@Beebom"
    ]


def fetch_competitor_data(api_key, handle, user_subs):
    try:
        cid = get_channel_id_from_handle(api_key, handle)
        if not cid:
            return None

        data = get_channel_stats(api_key, cid)
        subs = int(data['statistics'].get('subscriberCount', 0))
        if subs <= user_subs:
            return None

        videos = get_channel_videos(api_key, cid, 10)
        return parse_channel(data, videos)
    except:
        return None


# =====================================================
# 🔥 MAIN FUNCTION (USED BY FASTAPI)
# =====================================================

def main(api_key, channel_handle):

    channel_id = get_channel_id_from_handle(api_key, channel_handle)
    if not channel_id:
        return {"error": "Channel not found"}

    channel_data = get_channel_stats(api_key, channel_id)
    videos = get_channel_videos(api_key, channel_id, 15)
    user_channel = parse_channel(channel_data, videos)

    competitors = []
    handles = get_competitor_handles(user_channel['subscribers'])

    for h in handles:
        c = fetch_competitor_data(api_key, h, user_channel['subscribers'])
        if c:
            competitors.append(c)

    if not competitors:
        return {"error": "No competitors found"}

    comp_avg_views = np.mean([c['avg_views'] for c in competitors])
    comp_avg_likes = np.mean([c['avg_likes'] for c in competitors])
    comp_avg_eng = np.mean([c['engagement'] for c in competitors])

    return {
        "channel": {
            "name": user_channel["channel_name"],
            "subscribers": user_channel["subscribers"],
            "avg_views": user_channel["avg_views"],
            "avg_likes": user_channel["avg_likes"],
            "engagement": user_channel["engagement"]
        },
        "competitors_avg": {
            "avg_views": comp_avg_views,
            "avg_likes": comp_avg_likes,
            "engagement": comp_avg_eng
        },
        "charts": {
            "engagement_pie": {
                "labels": ["You", "Competitors"],
                "values": [
                    user_channel["engagement"],
                    comp_avg_eng
                ]
            },
            "views_bar": {
                "labels": ["You", "Competitors"],
                "values": [
                    user_channel["avg_views"],
                    comp_avg_views
                ]
            },
            "likes_bar": {
                "labels": ["You", "Competitors"],
                "values": [
                    user_channel["avg_likes"],
                    comp_avg_likes
                ]
            }
        }
    }
