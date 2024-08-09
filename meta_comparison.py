import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urlunparse
import csv

def normalize_url(url):
    """
    Normalize a URL by removing the scheme, netloc, and query parameters, and ensuring the path is consistent.
    """
    parsed_url = urlparse(url)
    normalized_path = parsed_url.path.rstrip('/')
    return urlunparse(('', '', normalized_path, '', '', ''))

def get_page_info(url):
    """
    Fetch the page and extract the title, meta title, meta description, and slug.
    """
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else ''
        meta_title = soup.find('meta', attrs={'name': 'title'})
        meta_title = meta_title['content'] if meta_title else ''
        meta_description = soup.find('meta', attrs={'name': 'description'})
        meta_description = meta_description['content'] if meta_description else ''
        slug = urlparse(url).path.rstrip('/').split('/')[-1]
        
        return {
            'url': url,
            'title': title,
            'meta_title': meta_title,
            'meta_description': meta_description,
            'slug': slug
        }
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None

def get_relative_urls(base_url, base_path, max_depth=3):
    session = requests.Session()
    visited = set()
    to_visit = {base_url}
    relative_urls = {}
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
        page_info = get_page_info(url)
        if page_info:
            normalized_url = normalize_url(url)
            relative_urls[normalized_url[len(base_path):]] = page_info
        
        try:
            response = session.get(url)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                parsed_href = urlparse(full_url)
                
                if parsed_href.netloc == '' or parsed_href.netloc == urlparse(base_url).netloc:
                    normalized_url = normalize_url(full_url)
                    if normalized_url.startswith(base_path) and full_url not in visited and full_url not in to_visit:
                        to_visit.add(full_url)
                        depth[full_url] = current_depth + 1
        except requests.RequestException as e:
            print(f"Failed to fetch {url}: {e}")

    print(f"Finished crawl on {base_url}")
    return relative_urls

def compare_urls(site1, base_path1, site2, base_path2, output_file):
    print(f"Crawling {site1}...")
    urls_site1 = get_relative_urls(site1, base_path1)
    print(f"Found {len(urls_site1)} URLs on {site1}")

    print(f"Crawling {site2}...")
    urls_site2 = get_relative_urls(site2, base_path2)
    print(f"Found {len(urls_site2)} URLs on {site2}")

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['URL on Site 1', 'Title 1', 'Meta Title 1', 'Meta Description 1', 'Slug 1',
                      'URL on Site 2', 'Title 2', 'Meta Title 2', 'Meta Description 2', 'Slug 2']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for relative_url, info1 in urls_site1.items():
            info2 = urls_site2.get(relative_url, {})
            writer.writerow({
                'URL on Site 1': info1.get('url', ''),
                'Title 1': info1.get('title', ''),
                'Meta Title 1': info1.get('meta_title', ''),
                'Meta Description 1': info1.get('meta_description', ''),
                'Slug 1': info1.get('slug', ''),
                'URL on Site 2': info2.get('url', ''),
                'Title 2': info2.get('title', ''),
                'Meta Title 2': info2.get('meta_title', ''),
                'Meta Description 2': info2.get('meta_description', ''),
                'Slug 2': info2.get('slug', '')
            })

# Define your site URLs and output file
site1 = 'http://localhost/thelowdown/wp/'
base_path1 = '/thelowdown/wp'
site2 = 'https://blog.thelowdown.com/'
base_path2 = '/'

output_file = 'url_comparison_results.csv'

compare_urls(site1, base_path1, site2, base_path2, output_file)
