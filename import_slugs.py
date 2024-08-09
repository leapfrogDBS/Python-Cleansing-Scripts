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

def get_current_slug(post_id):
    """
    Fetch the current slug of a post using the REST API.
    """
    response = requests.get(f"{SITE_URL}/wp-json/wp/v2/posts/{post_id}", auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD))
    if response.status_code == 200:
        return response.json().get('slug')
    else:
        print(f"Failed to fetch post data for post ID {post_id}: {response.status_code}, {response.text}")
        return None

def update_post_slug(post_id, new_slug):
    """
    Update post slug using the REST API.
    """
    current_slug = get_current_slug(post_id)
    if current_slug is None:
        print(f"Skipping update for post ID {post_id} due to fetch error.")
        return

    if current_slug != new_slug:
        data = {"slug": new_slug}
        response = requests.post(
            f"{SITE_URL}/wp-json/wp/v2/posts/{post_id}",
            json=data,
            auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
        )
        if response.status_code == 200:
            print(f"Successfully updated slug for post ID {post_id} to {new_slug}")
        else:
            print(f"Failed to update slug for post ID {post_id}: {response.status_code}, {response.text}")
    else:
        print(f"Slug for post ID {post_id} is already correct. Skipping update.")

def process_csv(file_path):
    """
    Process the CSV file and update the slugs for each post.
    """
    with open(file_path, mode='r', newline='', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        # Debugging: Print the headers
        print(f"CSV Headers: {csv_reader.fieldnames}")

        for row in csv_reader:
            try:
                post_id = int(row['post_id'])
                new_slug = row['post_slug']
                update_post_slug(post_id, new_slug)
            except KeyError as e:
                print(f"Missing expected column in CSV: {e}")
            except ValueError as e:
                print(f"Invalid data format: {e}")

# Check authentication
check_authentication()

# Process the CSV file (assumes the CSV file is in the same directory as the script)
process_csv('export_slugs.csv')
