import requests
import re
from requests.auth import HTTPBasicAuth

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

def fetch_all_posts():
    """
    Fetch all posts using the REST API.
    """
    posts = []
    page = 1
    while True:
        response = requests.get(
            f"{SITE_URL}/wp-json/wp/v2/posts",
            params={"per_page": 100, "page": page},
            auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
        )
        if response.status_code == 200:
            page_posts = response.json()
            if not page_posts:
                break
            posts.extend(page_posts)
            page += 1
        else:
            print(f"Failed to fetch posts: {response.status_code}, {response.text}")
            break
    return posts

def update_post_content(post_id, updated_content):
    """
    Update the post content using the REST API.
    """
    response = requests.post(
        f"{SITE_URL}/wp-json/wp/v2/posts/{post_id}",
        json={"content": updated_content},
        auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
    )
    if response.status_code == 200:
        print(f"Successfully updated post content for post {post_id}")
    else:
        print(f"Failed to update post content: {response.status_code}, {response.text}")

def clean_invalid_blocks(post_content):
    """
    Clean invalid blocks in the post content.
    """
    # Fix mismatched tags
    post_content = re.sub(r'</p>\s*<h2>(.*?)</h2>\s*<ul>(.*?)</ul>\s*<p>', r'<h2>\1</h2><ul>\2</ul>', post_content, flags=re.DOTALL)
    post_content = re.sub(r'<!-- wp:heading -->\s*<!-- /wp:heading -->', '', post_content)
    post_content = re.sub(r'<!-- wp:paragraph -->\s*<!-- /wp:paragraph -->', '', post_content)
    
    # Fix empty paragraphs
    post_content = re.sub(r'<!-- wp:paragraph -->\s*<p>\s*</p>\s*<!-- /wp:paragraph -->', '', post_content)
    
    return post_content

def process_post_content(post):
    """
    Process the post content: clean invalid blocks and update post content.
    """
    post_id = post['id']
    post_title = post['title']['rendered']
    post_content = post['content']['rendered']
    print(f"Processing post: {post_id} - {post_title}")

    # Print the fetched content for debugging
    print(f"Post content (first 500 chars): {post_content[:500]}...")

    # Clean invalid blocks
    cleaned_content = clean_invalid_blocks(post_content)
    if cleaned_content != post_content:
        print("Cleaned invalid blocks in post content.")
        update_post_content(post_id, cleaned_content)
    else:
        print("No invalid blocks found to clean.")

# Check authentication
check_authentication()

# Fetch all posts
all_posts = fetch_all_posts()
print(f"Found {len(all_posts)} posts to process.")

# Process each post
for post in all_posts:
    process_post_content(post)
