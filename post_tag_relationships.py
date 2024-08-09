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

def associate_tag_with_post(post_id, tag_id):
    """
    Associate a tag with a post using the REST API.
    """
    response = requests.get(f"{SITE_URL}/wp-json/wp/v2/posts/{post_id}", auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD))
    if response.status_code == 200:
        current_tags = response.json().get('tags', [])
        if tag_id not in current_tags:
            current_tags.append(tag_id)
            data = {"tags": current_tags}
            update_response = requests.post(
                f"{SITE_URL}/wp-json/wp/v2/posts/{post_id}",
                json=data,
                auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
            )
            if update_response.status_code == 200:
                print(f"Successfully associated tag ID {tag_id} with post ID {post_id}")
            else:
                print(f"Failed to associate tag ID {tag_id} with post ID {post_id}: {update_response.status_code}, {update_response.text}")
        else:
            print(f"Tag ID {tag_id} is already associated with post ID {post_id}")
    else:
        print(f"Failed to fetch post data for post ID {post_id}: {response.status_code}, {response.text}")

def import_post_tag_relationships(post_tag_relationships_csv):
    """
    Import post-tag relationships from a CSV file.
    """
    with open(post_tag_relationships_csv, mode='r', newline='', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            post_id = int(row['post_id'])
            tag_id = int(row['tag_id'])
            associate_tag_with_post(post_id, tag_id)

# Check authentication
check_authentication()

# Import post-tag relationships
import_post_tag_relationships('tag_relationship.csv')
