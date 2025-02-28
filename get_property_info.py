import os
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re
import concurrent.futures
import pandas as pd

project_path = Path(__file__).parents[0]
sys.path.append(os.path.abspath(project_path))


def load_urls():
    """
    Reads the links.csv file.
    Returns a list of the links to be scraped.
    """
    path = str(project_path)
    file = f"{path}/data/links.csv"
    with open(file, "r") as links_file:
        links_to_check = links_file.read().splitlines()

    return links_to_check


def collect_data(link: str) -> dict:
    """
    Scrapes the property data of the given url

    Parameters
    url -str: the link of the property to scrape

    Returns
    property_info -dict: dictionary containing the details of the property being sold
    """

    # Check that the linkis NOT for a real state project
    is_project = link.split("/")[-5]
    is_project = is_project.replace("-", " ")
    if "real estate project" in is_project:
        # skip
        return
    else:
        # Get the property's information

        # Set heathers to avoid target page's blocking
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        }
        # Send request
        req = requests.get(link, headers=headers)

        # Check status code is okay
        if req.status_code == 200:

            raw_property_info = {
                "id": None,
                "city": None,
                "p_type": None,
                "subtype": None,
                "price": 0,
                "nb_bedrooms": 0,
                "living_area": 0,
                "kitchen_type": 0,
                "furnished": 0,
                "open_fire": 0,
                "terrace": 0,
                "garden": 0,
                "land_surface": 0,
                "plot_surface": 0,
                "building_state": None,
                "facades": 0,
                "swim_pool": 0,
                "zip_code": 0,
                "year_of_construction": 0,
                "geolocation": None,
                "province": None,
            }

            # Get content and make soup
            content = req.content
            soup = BeautifulSoup(content, features="html.parser")

            # Property details are whithin the 8th <script> tag,
            # inside a variable called "av_items". Therefore:
            script = soup.find_all("script")[8].string

            # Apply regex to find the dictionary
            match = re.search(r"av_items\s*=\s*(\[\{.*?\}\])", script, re.DOTALL)

            # Get the details inside av_items
            av_items_str = match.group(1)

            # Convert to a list separating what will be each key-value pair
            av_items_list = av_items_str.split("\n")

            # Remove extra spaces and quotation marks in each list item
            av_items_list = [
                i.strip().replace('"', "").rstrip(",") for i in av_items_list
            ]

            # Remove unecessary brackets from first and last list items ('[' and ']')
            av_items_list.remove("[{")
            av_items_list.remove("}]")

            # Iterate over the list and collect relevant data
            for item in av_items_list:
                pair = item.split(":")
                # Remove extra spaces
                pair = [i.strip() for i in pair]
                # Collect the requested data:
                if pair[0] in [
                    "id",
                    "zip_code",
                    "subtype",
                    "price",
                    "nb_bedrooms",
                    "kitchen_type",
                    "land_surface",
                    "building_state",
                    "province",
                    "year_of_construction",
                    "geolocation",
                ]:
                    # Create a dict out of the two items in the pair list
                    pair_dict = dict([pair])
                    # Add it to the property_info dict
                    raw_property_info.update(pair_dict)

            # Adding missing data to the property info dict
            # city
            city = link.split("/")[-3]
            city = city.replace("-", " ")
            raw_property_info["city"] = city

            houses = (
                "house",
                "villa",
                "mansion",
                "town-house",
                "mixed-use-building",
                "exceptional-property",
            )
            appartments = (
                "apartment",
                "ground-floor",
                "penthouse",
                "flat-studio",
                "apartment-block",
                "duplex",
                "ground_floor",
            )

            # Create list of raw data from the table to find the missing data
            labels = [
                str(th) for th in soup.find_all("th", class_="classified-table__header")
            ]
            values = [
                str(td) for td in soup.find_all("td", class_="classified-table__data")
            ]

            # Get content of the extracted tags as labels to become keys
            new_labels = [
                re.search(r"<th.*?>(.*?)</th>", label, flags=re.DOTALL)
                for label in labels
            ]
            clean_labels = [
                new_label.group(1).strip() if new_label else "NA"
                for new_label in new_labels
            ]

            # Get content of the extracted tags as values to become values
            new_values = [
                re.search(r"<td[^>]*>(.*?)<", value, flags=re.DOTALL)
                for value in values
            ]
            clean_values = [
                new_value.group(1).strip() if new_value else "Not found"
                for new_value in new_values
            ]

            # Crate a dictionary with all the house details
            details_dict = {
                label: value for label, value in zip(clean_labels, clean_values)
            }

            # subtype
            subtype = raw_property_info["subtype"]
            raw_property_info["p_type"] = (
                "house"
                if subtype in houses
                else "apartment" if subtype in appartments else "other"
            )

            # living_area, furnished and open_fire
            raw_property_info["living_area"] = details_dict.get("Living area")
            raw_property_info["furnished"] = (
                1 if details_dict.get("Furnished") == "Yes" else 0
            )
            raw_property_info["open_fire"] = (
                1 if details_dict.get("How many fireplaces?") != None else 0
            )

            # Terrace
            terrace = details_dict.get("Terrace")
            terrace_area = details_dict.get("Terrace surface")
            raw_property_info["terrace"] = (
                terrace_area if terrace != None and terrace_area != None else 0
            )

            # Garden
            garden = details_dict.get("Garden")
            garden_area = details_dict.get("Garden surface")
            raw_property_info["garden"] = (
                garden_area if garden != None and garden_area != None else 0
            )

            # Plot surface
            plot_surface = details_dict.get("Surface of the plot")
            raw_property_info["plot_surface"] = (
                plot_surface if plot_surface not in [None, "''"] else 0
            )

            # Facades
            facades = details_dict.get("Number of frontages")
            raw_property_info["facades"] = facades if facades != None else 0

            # Swimming pool
            swim_pool = details_dict.get("Swimming pool")
            raw_property_info["swim_pool"] = (
                swim_pool if swim_pool not in ["No", None] else 0
            )

            # changing any empty strings to 0
            for key, value in raw_property_info.items():
                if value == "":
                    raw_property_info[key] = 0

            return raw_property_info


def concurrent_scraper(links_to_check):
    """
    Uses ThreadPoolExecutor to scrape multiple pages concurrently.
    Applies collect_data() function to each link in links_to_check.
    """
    scraped_properties = []

    # Using ThreadPoolExecutor for concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit tasks for each link
        future_to_link = {
            executor.submit(collect_data, link): link for link in links_to_check
        }
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_link):
            try:
                result = future.result()  # Get the result of collect_data(link)
                if result:
                    scraped_properties.append(result)
            except Exception as e:
                print(f"Error processing link {future_to_link[future]}: {e}")

    return scraped_properties


def save_to_csv(scraped_properties: list):
    """
    Converts the list of dictionaies containing the data
    of the properties into a pandas dictionary and saves it to
    a csv file.

    Parameters
    scraped_properties
    """
    df = pd.DataFrame(scraped_properties)
    df.to_csv(f"{project_path}/data/housing_market_data.csv", index=False)
    return df


if __name__ == "__main__":
    links_to_check = load_urls()[:2]
    # scraped_data = concurrent_scraper(links_to_check)
    # save_to_csv(scraped_data)
    print(len(links_to_check))
