import requests
import pandas as pd
import json
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup, Comment

# Replace these with your actual site URL, username, and application password
SITE_URL = "http://localhost/thelowdown/wp"
USERNAME = "dk.mcdonagh"
APPLICATION_PASSWORD = "pHKP aLUu sqpo dC25 AENp MUbQ"

def check_authentication():
    """
    Check if the provided username and application password are valid.
    """
    response = requests.get(f"{SITE_URL}/wp-json/wp/v2/users/me", auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD))
    if response.status_code == 200:
        print("Authentication successful.")
    else:
        print(f"Authentication failed: {response.status_code}, {response.text}")
        exit()

def fetch_all_post_ids():
    """
    Fetch all post IDs using the REST API.
    """
    post_ids = []
    page = 1
    while True:
        response = requests.get(
            f"{SITE_URL}/wp-json/wp/v2/posts",
            params={"per_page": 100, "page": page, "_fields": "id"},
            auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
        )
        if response.status_code == 200:
            page_posts = response.json()
            if not page_posts:
                break
            post_ids.extend([post['id'] for post in page_posts])
            page += 1
        elif response.status_code == 400 and "rest_post_invalid_page_number" in response.text:
            print("Reached the last page of posts.")
            break
        else:
            print(f"Failed to fetch posts: {response.status_code}, {response.text}")
            break
    return post_ids

def fetch_post(post_id):
    """
    Fetch the post content by post ID using the REST API.
    """
    response = requests.get(f"{SITE_URL}/wp-json/wp/v2/posts/{post_id}", auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch post: {response.status_code}")
        return None

def strip_html(content):
    """
    Strip HTML tags and comments from content.
    """
    soup = BeautifulSoup(content, "html.parser")
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    return soup.get_text()

def save_posts_to_json(posts, filename="blog_posts.json"):
    """
    Save the posts to a JSON file.
    """
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(posts, file, ensure_ascii=False, indent=4)
    print(f"Saved {len(posts)} posts to {filename}")

# Check authentication
check_authentication()

# Fetch all post IDs
post_ids = fetch_all_post_ids()
print(f"Found {len(post_ids)} posts to process.")

# Fetch each post content and prepare for JSON
posts = []
for post_id in post_ids:
    post = fetch_post(post_id)
    if post:
        posts.append({
            "ID": post["id"],
            "Title": post["title"]["rendered"],
            "Content": strip_html(post["content"]["rendered"])
        })

# Save all posts to JSON
save_posts_to_json(posts)
