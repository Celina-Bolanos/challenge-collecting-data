import os
import sys
from pathlib import Path
import concurrent.futures
import requests
from bs4 import BeautifulSoup

project_path = Path(__file__).parent
sys.path.append(os.path.abspath(project_path))

def get_page_links(page_number: int) -> list:
    """ 
    Collects urls to the individual properties listing.

    PARAMS
    page_number -int: page number of the target website containins property listings.

    RETURNS
    links -list: list of urls from where the information of each property is to be collected.
    """
    # Set heathers to avoid page's blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    }
    # Define targe url
    url = f'https://www.immoweb.be/en/search/house-and-apartment/for-sale?countries=BE&priceType=SALE_PRICE&page={page_number}&orderBy=relevance'

    # send request and get content
    req = requests.get(url, headers=headers)
    content = req.content

    # parse with beautiful soup and collect elements of type "a" (links)
    soup = BeautifulSoup(content, features='html.parser')
    page_links = soup.select('a.card__title-link[href*="classified"]')

    # start an empty list and extract only the urls
    collected_links = []
    for element in page_links:
        item_attrs = element.attrs
        link = item_attrs.get('href')
        collected_links.append(link)
    return collected_links


def save_data(collected_links):
    """ 
    Reads the links file to check for duplicates.
    Repeated links are skipped.
    New links are appended to the links.csv file.

    PARAMS
    links -list: list of collected urls
    """
    # Open csv file and read existing links
    with open(f'{project_path}/data/links.csv', 'r') as file:
        read_lines = set(file.readlines())

    # Start a new empty list where only no-repeated links are stored
    new_links_list = []
    
    # Check if link is repeated or not
    for link in collected_links:
        read_link = f'{link}\n' # new collected link that is being checked

        is_project = read_link.split('/')[-5]
        is_project = is_project.replace('-', ' ')
        if 'real estate project' in is_project:
            continue
        else:
            if read_link in read_lines: # check if link being checked is already in the csv file
                continue # If so, skip and go to the next link
            else:
                new_links_list.append(link) # Add to new, non repeated links list

    # Save new links to the links.csv file
    with open(f'{project_path}/data/links.csv', 'a') as file: 
        file.writelines([link + '\n' for link in new_links_list])

    #close the file
    file.close()

    # Print total new links collected.
    print(f'Total new links: {len(new_links_list)}')


# Function to apply concurrency once app is running in production // 
# Need to check if variable name 'links' that it returns should be changed for clarity
def concurrent_links_scraper():
    links = [] 
    # Using ThreadPoolExecutor to scrape multiple pages concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit tasks for each page (e.g., pages 1 to 333)
        future_to_page = {executor.submit(get_page_links, page+1): page+1 for page in range(1)}
    
        # Process results as they come in
        for future in concurrent.futures.as_completed(future_to_page):
            try:
                page_links = future.result()  # Get the result (links from the page)
                links.extend(page_links)  # Add links to the main hrefs list
            except Exception:
                continue
    return links



if __name__ == "__main__":
    links = concurrent_links_scraper()
    save_data(links)
