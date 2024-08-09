import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pandas as pd

def get_page_data(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Extract data
                page_title = soup.title.string if soup.title else 'N/A'
                slug = urlparse(url).path.strip('/').split('/')[-1]
                meta_title_tag = soup.find("meta", property="og:title")
                meta_title = meta_title_tag["content"] if meta_title_tag else 'N/A'
                meta_description_tag = soup.find("meta", attrs={"name": "description"})
                meta_description = meta_description_tag["content"] if meta_description_tag else 'N/A'
                canonical_url_tag = soup.find("link", rel="canonical")
                canonical_url = canonical_url_tag["href"] if canonical_url_tag else 'N/A'

                return {
                    "full_url": url,
                    "relative_url": urlparse(url).path,
                    "page_title": page_title,
                    "slug": slug,
                    "meta_title": meta_title,
                    "meta_description": meta_description,
                    "canonical_url": canonical_url
                }
            elif response.status_code == 404:
                print(f"404 Not Found: {url}")
                return None
            else:
                print(f"Failed to fetch {url} (status: {response.status_code})")
        except requests.Timeout:
            print(f"Timeout occurred for {url}, retrying ({attempt + 1}/{retries})")
        except requests.RequestException as e:
            print(f"Exception occurred while fetching {url}: {e}")
            break
    print(f"Giving up on {url} after {retries} retries")
    return None

def crawl_site(base_url, max_pages=-1, retries=3):
    session = requests.Session()
    visited = set()
    to_visit = {base_url}
    crawled_data = []

    print(f"Starting crawl on {base_url}")

    while to_visit and (len(crawled_data) < max_pages or max_pages == -1):
        url = to_visit.pop()
        if url in visited:
            continue

        visited.add(url)
        print(f"Visiting: {url}")
        page_data = get_page_data(url, retries=retries)
        if page_data:
            crawled_data.append(page_data)

        try:
            response = session.get(url, timeout=5)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == urlparse(base_url).netloc and full_url not in visited:
                    to_visit.add(full_url)

        except requests.Timeout:
            print(f"Timeout occurred for {url}, moving on")
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")

    print(f"Finished crawl on {base_url}")
    return crawled_data

def compare_sites(site1_data, site2_base_url, retries=3):
    for page_data in site1_data:
        relative_url = page_data["relative_url"]
        site2_url = site2_base_url + relative_url
        print(f"Inspecting URL: {site2_url}")
        site2_page_data = get_page_data(site2_url, retries=retries)
        if site2_page_data:
            page_data.update({
                "site2_full_url": site2_page_data["full_url"],
                "site2_relative_url": relative_url,
                "site2_page_title": site2_page_data["page_title"],
                "site2_slug": site2_page_data["slug"].split('/')[-1],
                "site2_meta_title": site2_page_data["meta_title"],
                "site2_meta_description": site2_page_data["meta_description"],
                "site2_canonical_url": site2_page_data["canonical_url"]
            })
        else:
            page_data.update({
                "site2_full_url": 'N/A',
                "site2_relative_url": relative_url,
                "site2_page_title": 'N/A',
                "site2_slug": 'N/A',
                "site2_meta_title": 'N/A',
                "site2_meta_description": 'N/A',
                "site2_canonical_url": 'N/A'
            })
    return site1_data

def save_to_csv(data, output_file):
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

# Define your site URLs and output file
site1_url = 'https://blog.thelowdown.com/'
site2_base_url = 'http://localhost/thelowdown/wp'
output_file = 'page_data_comparison.csv'

# User input for number of pages to crawl
max_pages = int(input("Enter the number of pages to crawl (-1 for no limit): "))

# Crawl the first site and get data
crawled_site1_data = crawl_site(site1_url, max_pages=max_pages)

# Compare with the second site
comparison_data = compare_sites(crawled_site1_data, site2_base_url)

# Save the comparison data to a CSV file
save_to_csv(comparison_data, output_file)
