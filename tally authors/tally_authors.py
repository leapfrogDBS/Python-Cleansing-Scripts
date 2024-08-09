import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import pandas as pd

def get_page_data_site1(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                column_author = soup.find(class_='column-author')
                written_by = 'N/A'
                reviewed_by = 'N/A'

                if column_author:
                    # Find all anchor tags in the column-author div that are not within an image tag
                    author_links = [
                        link for link in column_author.find_all('a', href=True)
                        if not link.find('img')
                    ]
                    authors = [link.get_text().strip() for link in author_links]

                    if len(authors) > 0:
                        written_by = authors[0]
                    if len(authors) > 1:
                        reviewed_by = authors[1]

                return {
                    "full_url": url,
                    "written_by": written_by,
                    "reviewed_by": reviewed_by,
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

def get_page_data_site2(url, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                authors = []
                by_tags = soup.find_all(text=lambda text: text and 'by' in text.lower())
                for by_tag in by_tags:
                    by_link = by_tag.find_next('a')
                    if by_link:
                        author_name = by_link.get_text()
                        if author_name not in authors:
                            authors.append(author_name)

                written_by = authors[0] if len(authors) > 0 else 'N/A'
                reviewed_by = authors[1] if len(authors) > 1 else 'N/A'

                return {
                    "full_url": url,
                    "written_by": written_by,
                    "reviewed_by": reviewed_by,
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

def crawl_site(base_url, get_page_data_func, max_pages=10, retries=3):
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
        page_data = get_page_data_func(url, retries=retries)
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
    comparison_data = []
    for page_data in site1_data:
        relative_url = urlparse(page_data["full_url"]).path
        site2_url = site2_base_url + relative_url
        print(f"Inspecting URL: {site2_url}")
        site2_page_data = get_page_data_site2(site2_url, retries=retries)
        comparison_data.append({
            "site1_url": page_data["full_url"],
            "site1_written_by": page_data["written_by"],
            "site1_reviewed_by": page_data["reviewed_by"],
            "site2_url": site2_url,
            "site2_written_by": site2_page_data["written_by"] if site2_page_data else 'N/A',
            "site2_reviewed_by": site2_page_data["reviewed_by"] if site2_page_data else 'N/A',
        })
    return comparison_data

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
crawled_site1_data = crawl_site(site1_url, get_page_data_site1, max_pages=max_pages)

# Compare with the second site
comparison_data = compare_sites(crawled_site1_data, site2_base_url)

# Save the comparison data to a CSV file
save_to_csv(comparison_data, output_file)
