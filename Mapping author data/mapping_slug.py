import csv
import requests
from requests.auth import HTTPBasicAuth

# Replace these with your actual site URL, username, and application password for the development site
DEV_SITE_URL = "http://localhost/thelowdown/wp"
USERNAME = "dk.mcdonagh"
APPLICATION_PASSWORD = "pHKP aLUu sqpo dC25 AENp MUbQ"
CUSTOM_POST_TYPE = "contributor"  # Custom post type name

def check_authentication():
    """
    Check if the provided username and application password are valid.
    """
    response = requests.get(f"{DEV_SITE_URL}/wp-json/wp/v2/users/me", auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD))
    if response.status_code == 200:
        print("Authentication successful.")
    else:
        print(f"Authentication failed: {response.status_code}, {response.text}")
        exit()

def get_current_slug(post_id):
    """
    Fetch the current slug of a post using the REST API.
    """
    try:
        response = requests.get(f"{DEV_SITE_URL}/wp-json/wp/v2/{CUSTOM_POST_TYPE}/{post_id}", auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD))
        if response.status_code == 200:
            return response.json().get('slug')
        else:
            print(f"Failed to fetch post data for post ID {post_id}: {response.status_code}, {response.text}")
            return None
    except requests.RequestException as e:
        print(f"Exception occurred while fetching post data for post ID {post_id}: {e}")
        return None

def update_post_slug(post_id, slug):
    """
    Update post slug using the REST API.
    """
    try:
        data = {"slug": slug}
        response = requests.post(
            f"{DEV_SITE_URL}/wp-json/wp/v2/{CUSTOM_POST_TYPE}/{post_id}",
            json=data,
            auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
        )
        if response.status_code == 200:
            print(f"Successfully updated slug for post ID {post_id}")
        else:
            print(f"Failed to update slug for post ID {post_id}: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Exception occurred while updating slug for post ID {post_id}: {e}")

def process_slugs(slugs_file, post_id_mapping_file):
    """
    Process slugs and update corresponding posts in the development site.
    """
    post_id_mapping = {}
    with open(post_id_mapping_file, mode='r', newline='', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            post_id_mapping[int(row['prod_post_id'])] = int(row['dev_post_id'])

    with open(slugs_file, mode='r', newline='', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            prod_post_id = int(row['post_id'])
            slug = row['post_slug']
            if prod_post_id in post_id_mapping:
                dev_post_id = post_id_mapping[prod_post_id]
                current_slug = get_current_slug(dev_post_id)
                if current_slug is None:
                    print(f"Skipping post ID {dev_post_id} due to fetch error.")
                    continue
                if current_slug != slug:
                    update_post_slug(dev_post_id, slug)

# Check authentication
check_authentication()

# Process slugs and update development posts
process_slugs('slugs.csv', 'mapping.csv')
