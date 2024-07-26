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

def update_acf_fields(post_id, list_items, field_name):
    """
    Update ACF fields using the REST API.
    """
    acf_data = {"acf": {field_name: [{"reference": item} for item in list_items]}}
    print(f"Updating post {post_id} with ACF data: {acf_data}")
    response = requests.post(
        f"{SITE_URL}/wp-json/wp/v2/posts/{post_id}",
        json=acf_data,
        auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
    )
    if response.status_code == 200:
        print(f"Successfully updated ACF fields for post {post_id}")
    else:
        print(f"Failed to update ACF fields: {response.status_code}, {response.text}")

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

def process_post_content(post_id):
    """
    Process the post content: extract list items, update ACF fields, and remove blocks.
    """
    post = fetch_post(post_id)
    if not post:
        return

    post_id = post['id']
    post_title = post['title']['rendered']
    post_content = post['content']['rendered']
    print(f"Processing post: {post_id} - {post_title}")

    # Regex to find ordered lists without a "References" title
    pattern = r'(<ol class="wp-block-list">.*?</ol>)'
    matches = re.findall(pattern, post_content, flags=re.DOTALL | re.IGNORECASE)

    if matches:
        for match in matches:
            list_block = match

            # Extract list items
            list_items = re.findall(r'<li>(.*?)</li>', list_block, flags=re.DOTALL | re.IGNORECASE)
            if list_items:
                print(f"Post title: {post_title}")
                print(f"Found list block:\n{list_block}\n")
                user_input = input("Do you want to process this list and move to references? (Y/N): ")
                if user_input.lower() == 'y':
                    # Update ACF fields
                    update_acf_fields(post_id, list_items, 'references')

                    # Remove the matched blocks from the content
                    updated_content = post_content.replace(list_block, '')
                    update_post_content(post_id, updated_content)
            else:
                print("No list items found in the matched list block.")
    else:
        print("No matching lists found.")

# Check authentication
check_authentication()

# Fetch all post IDs
post_ids = fetch_all_post_ids()
print(f"Found {len(post_ids)} posts to process.")

# Process each post
for post_id in post_ids:
    process_post_content(post_id)
