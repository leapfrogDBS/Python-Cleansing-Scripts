import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

def get_relative_urls(base_url, max_depth=3):
    session = requests.Session()
    visited = set()
    to_visit = {base_url}
    relative_urls = set()
    depth = {base_url: 0}

    print(f"Starting crawl on {base_url}")

    while to_visit:
        url = to_visit.pop()
        current_depth = depth[url]

        if current_depth > max_depth:
            continue

        if url in visited:
            continue

        visited.add(url)
        try:
            response = session.get(url)
            print(f"Fetched {url} (status: {response.status_code})")
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                parsed_href = urlparse(href)

                if parsed_href.netloc == '' or parsed_href.netloc == urlparse(base_url).netloc:
                    if parsed_href.path.startswith('/'):
                        relative_urls.add(parsed_href.path)
                        full_url = urljoin(base_url, href)
                        if full_url not in visited and full_url not in to_visit:
                            to_visit.add(full_url)
                            depth[full_url] = current_depth + 1
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")

    print(f"Finished crawl on {base_url}")
    return relative_urls

def compare_urls(site1, site2):
    print(f"Crawling {site1}...")
    urls_site1 = get_relative_urls(site1)
    print(f"Found {len(urls_site1)} URLs on {site1}")

    print(f"Crawling {site2}...")
    urls_site2 = get_relative_urls(site2)
    print(f"Found {len(urls_site2)} URLs on {site2}")

    missing_in_site2 = urls_site1 - urls_site2
    missing_in_site1 = urls_site2 - urls_site1

    print("\nURLs in site 1 but not in site 2:")
    for url in missing_in_site2:
        print(url)

    print("\nURLs in site 2 but not in site 1:")
    for url in missing_in_site1:
        print(url)

# Define your site URLs
site1 = 'http://localhost/thelowdown/wp/'
site2 = 'https://blog.thelowdown.com/'

compare_urls(site1, site2)
