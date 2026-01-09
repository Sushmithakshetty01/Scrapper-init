import requests
import time
import matplotlib.pyplot as plt
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

def run_instagram_scraper(api_key, usernames, results_limit=100):
    """Run Apify Instagram profile scraper"""
    url = "https://api.apify.com/v2/acts/apify~instagram-profile-scraper/runs"

    payload = {
        "usernames": usernames,
        "resultsLimit": results_limit,
        "maxPosts": 100,
        "addParentData": False
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    response.raise_for_status()

    run_data = response.json()
    run_id = run_data['data']['id']

    return wait_for_completion(api_key, run_id)

def wait_for_completion(api_key, run_id):
    """Wait for scraper to finish"""
    url = f"https://api.apify.com/v2/acts/apify~instagram-profile-scraper/runs/{run_id}"
    headers = {"Authorization": f"Bearer {api_key}"}

    for _ in range(60):
        response = requests.get(url, headers=headers, timeout=30)
        run_info = response.json()
        status = run_info['data']['status']

        if status == "SUCCEEDED":
            dataset_id = run_info['data']['defaultDatasetId']
            return get_dataset(api_key, dataset_id)
        elif status in ["FAILED", "ABORTED", "TIMED-OUT"]:
            return None

        time.sleep(5)

    return None

def get_dataset(api_key, dataset_id):
    """Get scraper results"""
    url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
    headers = {"Authorization": f"Bearer {api_key}"}

    response = requests.get(url, headers=headers, timeout=30)
    return response.json()

def parse_date_filter(date_input):
    """Parse date filter input"""
    if not date_input or date_input.lower() == 'all':
        return None, None

    today = datetime.now()

    if date_input.lower() == 'today':
        return today.replace(hour=0, minute=0, second=0), today
    elif date_input.lower() == 'yesterday':
        yesterday = today - timedelta(days=1)
        return yesterday.replace(hour=0, minute=0, second=0), yesterday.replace(hour=23, minute=59, second=59)
    elif date_input.lower().endswith('days'):
        try:
            days = int(date_input.lower().replace('days', '').strip())
            start_date = today - timedelta(days=days)
            return start_date, today
        except:
            pass
    elif date_input.lower().endswith('weeks'):
        try:
            weeks = int(date_input.lower().replace('weeks', '').strip())
            start_date = today - timedelta(weeks=weeks)
            return start_date, today
        except:
            pass
    elif date_input.lower().endswith('months'):
        try:
            months = int(date_input.lower().replace('months', '').strip())
            start_date = today - timedelta(days=months*30)
            return start_date, today
        except:
            pass

    if ' to ' in date_input:
        try:
            start_str, end_str = date_input.split(' to ')
            start_date = datetime.strptime(start_str.strip(), '%Y-%m-%d')
            end_date = datetime.strptime(end_str.strip(), '%Y-%m-%d')
            return start_date, end_date
        except:
            pass

    return None, None

def filter_posts_by_date(posts, start_date, end_date):
    """Filter posts by date"""
    if not start_date and not end_date:
        return posts

    filtered = []
    for post in posts:
        post_timestamp = post.get('timestamp')
        if not post_timestamp:
            continue

        try:
            if isinstance(post_timestamp, str):
                post_date = datetime.fromisoformat(post_timestamp.replace('Z', '+00:00'))
            else:
                post_date = datetime.fromtimestamp(post_timestamp)

            post_date = post_date.replace(tzinfo=None)

            if start_date and post_date < start_date:
                continue
            if end_date and post_date > end_date:
                continue

            filtered.append(post)
        except:
            filtered.append(post)

    return filtered

def detect_topic(caption, hashtags):
    """Detect post topic"""
    text = (caption + ' ' + ' '.join(hashtags)).lower()

    topics = {
        'fashion': ['fashion', 'style', 'outfit', 'ootd', 'dress', 'wear', 'clothing', 'fashionista', 'stylish', 'lookbook'],
        'beauty': ['beauty', 'makeup', 'skincare', 'cosmetic', 'glam', 'makeupartist', 'beautytips', 'lipstick', 'foundation'],
        'fitness': ['fitness', 'workout', 'gym', 'exercise', 'fit', 'training', 'health', 'muscle', 'fitfam', 'bodybuilding'],
        'travel': ['travel', 'trip', 'vacation', 'wanderlust', 'explore', 'adventure', 'destination', 'tourism', 'traveling'],
        'food': ['food', 'foodie', 'recipe', 'cooking', 'delicious', 'yummy', 'eat', 'cuisine', 'meal', 'dish'],
        'lifestyle': ['lifestyle', 'life', 'daily', 'vlog', 'blogger', 'influencer', 'content', 'creator', 'inspo']
    }

    topic_scores = {}
    for topic, keywords in topics.items():
        score = sum(1 for keyword in keywords if keyword in text)
        if score > 0:
            topic_scores[topic] = score

    if topic_scores:
        return max(topic_scores, key=topic_scores.get)

    return 'lifestyle'

def parse_profile(profile, start_date=None, end_date=None, api_key=None):
    """Parse Instagram profile data"""
    followers = profile.get('followersCount', 0)
    posts = profile.get('latestPosts', [])

    if followers == 0:
        return None

    if start_date or end_date:
        posts = filter_posts_by_date(posts, start_date, end_date)

    all_reels = []
    for post in posts:
        is_video = (
            post.get('type') == 'Video' or
            post.get('type') == 'Reel' or
            post.get('videoViewCount', 0) > 0 or
            post.get('videoPlayCount', 0) > 0 or
            post.get('isVideo', False) or
            'Video' in str(post.get('productType', ''))
        )

        if is_video:
            all_reels.append(post)

    top_reels = all_reels[:10]

    total_likes = sum(p.get('likesCount', 0) for p in posts[:10]) if posts else 0
    total_comments = sum(p.get('commentsCount', 0) for p in posts[:10]) if posts else 0

    post_count = min(len(posts), 10)
    avg_likes = total_likes // post_count if post_count > 0 else 0
    avg_comments = total_comments // post_count if post_count > 0 else 0

    engagement = round(((avg_likes + avg_comments) / followers) * 100, 2) if followers > 0 else 0

    parsed_reels = []
    for post in top_reels:
        caption = post.get('caption', '')
        hashtags = re.findall(r'#\w+', caption)
        topic = detect_topic(caption, hashtags)

        parsed_reels.append({
            'caption': caption[:200],
            'likes': post.get('likesCount', 0),
            'comments': post.get('commentsCount', 0),
            'views': post.get('videoViewCount', 0) or post.get('videoPlayCount', 0) or 0,
            'hashtags': hashtags[:10],
            'topic': topic,
            'url': f"https://instagram.com/p/{post.get('shortCode', '')}",
            'timestamp': post.get('timestamp')
        })

    parsed_posts = []
    for post in posts[:50]:
        caption = post.get('caption', '')
        hashtags = re.findall(r'#\w+', caption)
        topic = detect_topic(caption, hashtags)

        parsed_posts.append({
            'caption': caption[:200],
            'likes': post.get('likesCount', 0),
            'comments': post.get('commentsCount', 0),
            'views': post.get('videoViewCount', 0) or post.get('videoPlayCount', 0) or 0,
            'hashtags': hashtags[:10],
            'topic': topic,
            'url': f"https://instagram.com/p/{post.get('shortCode', '')}",
            'timestamp': post.get('timestamp')
        })

    return {
        'username': profile.get('username', ''),
        'name': profile.get('fullName', ''),
        'followers': followers,
        'posts_count': profile.get('postsCount', 0),
        'engagement': engagement,
        'avg_likes': avg_likes,
        'avg_comments': avg_comments,
        'posts': parsed_posts,
        'top_reels': parsed_reels,
        'total_reels_count': len(all_reels),
        'verified': profile.get('verified', False)
    }

def get_competitor_list(user_followers):
    """Get competitor usernames based on follower tier"""
    if user_followers >= 1_000_000:
        return ['leoniehanne', 'aimeesong', 'hudabeauty']
    elif user_followers >= 100_000:
        return ['stylebook', 'fashiongoalsz', 'beautyblogger']
    else:
        return ['lifestyleblogger', 'fashionista', 'styleinspo']

# =========================================================
# FASTAPI WRAPPER (ADDED – EXISTING CODE UNTOUCHED)
# =========================================================

def analyze_instagram(api_key: str, username: str, date_input: str | None = None):
    start_date, end_date = parse_date_filter(date_input)

    user_data = run_instagram_scraper(api_key, [username], 100)
    if not user_data:
        raise Exception("Could not fetch Instagram profile")

    user_profile = parse_profile(user_data[0], start_date, end_date, api_key)
    if not user_profile:
        raise Exception("Could not parse Instagram profile")

    competitor_usernames = get_competitor_list(user_profile['followers'])
    competitors = []
    total_reels_collected = 0

    for i in range(0, len(competitor_usernames), 10):
        batch = competitor_usernames[i:i+10]
        batch_data = run_instagram_scraper(api_key, batch, 100)

        if batch_data:
            for profile_data in batch_data:
                parsed = parse_profile(profile_data, start_date, end_date, api_key)
                if parsed and parsed['followers'] > user_profile['followers']:
                    competitors.append(parsed)
                    total_reels_collected += len(parsed['top_reels'])

        if total_reels_collected >= 100:
            break

        time.sleep(3)

    return {
        "user_profile": user_profile,
        "competitors": competitors,
        "competitor_count": len(competitors),
        "total_reels_collected": total_reels_collected
    }
