import requests
import re
import os
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

# Take links to remote images, save locally and update reference

# Configuration
SITE_URL = "http://localhost/thelowdown/wp"
USERNAME = "dk.mcdonagh"
APPLICATION_PASSWORD = "pHKP aLUu sqpo dC25 AENp MUbQ"
POST_IDS = [54597, 54601, 54606, 54620, 54625, 54630, 54634, 54638, 54642, 54646]  # Replace with the list of specific post IDs
original_site_url = 'https://blog.thelowdown.com'  # Replace with the original site URL

# Check authentication
def check_authentication():
    response = requests.get(f"{SITE_URL}/wp-json/wp/v2/users/me", auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD))
    if response.status_code == 200:
        print("Authentication successful.")
    else:
        print(f"Authentication failed: {response.status_code}, {response.text}")
        exit()

# Fetch the post content by post ID using the REST API
def fetch_post(post_id):
    response = requests.get(f"{SITE_URL}/wp-json/wp/v2/posts/{post_id}", auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD))
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch post: {response.status_code}")
        return None

# Update the post content using the REST API
def update_post_content(post_id, updated_content):
    response = requests.post(
        f"{SITE_URL}/wp-json/wp/v2/posts/{post_id}",
        json={"content": updated_content},
        auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
    )
    if response.status_code == 200:
        print(f"Successfully updated post content for post {post_id}")
    else:
        print(f"Failed to update post content: {response.status_code}, {response.text}")

# Process the post content
def process_post_content(post_id):
    post = fetch_post(post_id)
    if not post:
        return

    post_content = post['content']['rendered']
    soup = BeautifulSoup(post_content, 'html.parser')
    images = soup.find_all('img')

    if not images:
        print(f"No images found in post {post_id}.")
        return

    for img in images:
        img_url = img['src']
        if original_site_url in img_url:
            print(f"Processing image: {img_url}")
            img_filename = os.path.basename(img_url)
            img_data = requests.get(img_url).content

            # Save the image to a temporary local file
            local_img_path = f"/tmp/{img_filename}"
            with open(local_img_path, 'wb') as img_file:
                img_file.write(img_data)
            print(f"Image saved locally: {local_img_path}")

            # Upload the image to the new site
            with open(local_img_path, 'rb') as img_file:
                media_response = requests.post(
                    f"{SITE_URL}/wp-json/wp/v2/media",
                    headers={
                        'Content-Disposition': f'attachment; filename={img_filename}'
                    },
                    files={
                        'file': img_file
                    },
                    auth=HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
                )

            if media_response.status_code == 201:
                new_img_url = media_response.json().get('source_url')
                post_content = post_content.replace(img_url, new_img_url)
                print(f"Image uploaded: {new_img_url}")
            else:
                print(f'Failed to upload image: {media_response.status_code}, {media_response.text}')

    # Update the post content with the new image URLs
    update_post_content(post_id, post_content)

# Check authentication
check_authentication()

# Process each post in the list
for post_id in POST_IDS:
    process_post_content(post_id)
