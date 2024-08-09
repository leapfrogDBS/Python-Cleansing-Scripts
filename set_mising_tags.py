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

def get_current_tags():
    """
    Fetch all current tags using the REST API.
    """
    tags = {}
    page = 1
    while True:
        response = requests.get(
            f"{SITE_URL}/wp-json/wp/v2/tags",
            params={"per_page": 100, "page": page},
            auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
        )
        if response.status_code == 200:
            page_tags = response.json()
            if not page_tags:
                break
            for tag in page_tags:
                tags[tag['slug']] = tag['id']
            page += 1
        else:
            print(f"Failed to fetch tags: {response.status_code}, {response.text}")
            break
    return tags

def create_tag(name, slug):
    """
    Create a new tag using the REST API.
    """
    data = {"name": name, "slug": slug}
    response = requests.post(
        f"{SITE_URL}/wp-json/wp/v2/tags",
        json=data,
        auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
    )
    if response.status_code == 201:
        tag_id = response.json()['id']
        print(f"Successfully created tag '{name}' with ID {tag_id}")
        return tag_id
    else:
        print(f"Failed to create tag '{name}': {response.status_code}, {response.text}")
        return None

def import_missing_tags(tags_csv):
    """
    Import missing tags from a CSV file and return the IDs of newly created tags.
    """
    current_tags = get_current_tags()
    new_tag_ids = {}

    with open(tags_csv, mode='r', newline='', encoding='utf-8-sig') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            term_id = int(row['term_id'])
            name = row['name']
            slug = row['slug']

            if slug not in current_tags:
                new_tag_id = create_tag(name, slug)
                if new_tag_id:
                    new_tag_ids[term_id] = new_tag_id

    return new_tag_ids

# Check authentication
check_authentication()

# Import missing tags and get new tag IDs
new_tag_ids = import_missing_tags('cat_terms.csv')
print("New tag IDs:", new_tag_ids)
