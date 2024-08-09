import csv
import requests
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

def fetch_post_ids():
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

def get_current_post_data(post_id):
    """
    Fetch the current post data using the REST API.
    """
    response = requests.get(f"{SITE_URL}/wp-json/wp/v2/posts/{post_id}", auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch post data for post ID {post_id}: {response.status_code}, {response.text}")
        return None

def update_post_slug(post_id, post_slug):
    """
    Update post slug using the REST API.
    """
    current_data = get_current_post_data(post_id)
    if current_data and current_data.get('slug') != post_slug:
        data = {"slug": post_slug}
        response = requests.post(
            f"{SITE_URL}/wp-json/wp/v2/posts/{post_id}",
            json=data,
            auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
        )
        if response.status_code == 200:
            print(f"Successfully updated slug for post ID {post_id} to {post_slug}")
        else:
            print(f"Failed to update slug for post ID {post_id}: {response.status_code}, {response.text}")
    else:
        print(f"Slug for post ID {post_id} is already correct. Skipping update.")

def update_yoast_meta(post_id, meta_key, meta_value):
    """
    Update Yoast SEO meta fields using the REST API.
    """
    current_data = get_current_post_data(post_id)
    if current_data:
        current_meta = current_data.get('meta', {})
        if current_meta.get(meta_key) != meta_value:
            data = {"meta": {meta_key: meta_value}}
            response = requests.post(
                f"{SITE_URL}/wp-json/wp/v2/posts/{post_id}",
                json=data,
                auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
            )
            if response.status_code == 200:
                print(f"Successfully updated {meta_key} for post ID {post_id}")
            else:
                print(f"Failed to update {meta_key} for post ID {post_id}: {response.status_code}, {response.text}")
        else:
            print(f"{meta_key} for post ID {post_id} is already correct. Skipping update.")
    else:
        print(f"Failed to retrieve current data for post ID {post_id}. Skipping update.")

def process_csv(file_path):
    """
    Process the CSV file and update the Yoast SEO meta fields and post slugs for each post.
    """
    post_ids = fetch_post_ids()
    print(f"Fetched {len(post_ids)} post IDs from the site.")

    with open(file_path, mode='r', newline='', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        # Debugging: Print the headers
        print(f"CSV Headers: {csv_reader.fieldnames}")

        post_meta_updates = {}

        for row in csv_reader:
            try:
                post_id = int(row['post_id'])
                meta_key = row['meta_key']
                meta_value = row['meta_value']
                
                # Check if the post ID exists
                if post_id in post_ids:
                    if post_id not in post_meta_updates:
                        post_meta_updates[post_id] = {}
                    post_meta_updates[post_id][meta_key] = meta_value
                else:
                    print(f"Post ID {post_id} does not exist. Skipping...")
            except KeyError as e:
                print(f"Missing expected column in CSV: {e}")
            except ValueError as e:
                print(f"Invalid data format: {e}")

        for post_id, meta_updates in post_meta_updates.items():
            current_meta = get_current_post_data(post_id)
            if current_meta is None:
                continue

            current_meta_values = current_meta.get('meta', {})
            for meta_key, meta_value in meta_updates.items():
                if meta_key == '_yoast_wpseo_slug':
                    update_post_slug(post_id, meta_value)
                else:
                    if current_meta_values.get(meta_key) != meta_value:
                        update_yoast_meta(post_id, meta_key, meta_value)
                    else:
                        print(f"{meta_key} for post ID {post_id} is already correct. Skipping update.")

# Check authentication
check_authentication()

# Process the CSV file (assumes the CSV file is in the same directory as the script)
process_csv('exported_data.csv')
