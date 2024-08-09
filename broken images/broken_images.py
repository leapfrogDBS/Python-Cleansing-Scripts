import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urlparse, urljoin
import time

def get_page(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response
        except requests.Timeout:
            print(f"Timeout occurred for {url}, retrying ({attempt + 1}/{retries})")
        except requests.RequestException as e:
            print(f"Exception occurred while fetching {url}: {e}")
            time.sleep(2)  # wait before retrying
    print(f"Giving up on {url} after {retries} retries")
    return None

def get_all_links(url, domain, retries=3):
    links = set()
    response = get_page(url, retries)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith(('http', 'https')):
                link_url = href
            else:
                link_url = urljoin(url, href)
            
            parsed_link_url = urlparse(link_url)
            if parsed_link_url.netloc == domain:
                links.add(link_url)
    return links

def crawl_site(start_url, retries=3):
    parsed_start_url = urlparse(start_url)
    domain = parsed_start_url.netloc
    to_crawl = set([start_url])
    crawled = set()
    
    while to_crawl:
        url = to_crawl.pop()
        if url not in crawled:
            print(f"Crawling: {url}")
            crawled.add(url)
            new_links = get_all_links(url, domain, retries)
            print(f"Found {len(new_links)} links on {url}")
            to_crawl.update(new_links - crawled)
            time.sleep(1)  # to avoid overwhelming the server
    
    return crawled

def check_broken_images(url, retries=3):
    print(f"Checking page: {url}")
    broken_images = []
    response = get_page(url, retries)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')

        for img in images:
            img_url = img.get('src')
            if not img_url.startswith(('http:', 'https:')):
                img_url = urljoin(url, img_url)

            img_response = get_page(img_url, retries)
            if img_response and img_response.status_code != 200:
                broken_images.append((url, img_url, img_response.status_code))
            elif not img_response:
                broken_images.append((url, img_url, 'Failed to fetch'))
    return broken_images

def save_to_csv(broken_images, filename='broken_images.csv'):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Page URL", "Image URL", "Status"])
        writer.writerows(broken_images)
    print(f"Broken images have been saved to {filename}")

if __name__ == "__main__":
    start_url = input("Enter the URL of the website to check for broken images: ")
    print(f"Starting crawl on: {start_url}")
    all_urls = crawl_site(start_url)
    print(f"Total pages found: {len(all_urls)}")

    all_broken_images = []
    
    for url in all_urls:
        broken_images = check_broken_images(url)
        all_broken_images.extend(broken_images)
    
    if all_broken_images:
        save_to_csv(all_broken_images)
    else:
        print("No broken images found.")
