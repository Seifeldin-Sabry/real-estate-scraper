from enums.enums import SortBy
from model.property import Property
from scrape.util import construct_url
from settings.application_settings import settings
import requests
from bs4 import BeautifulSoup


def get_properties() -> list[Property]:
    """
    Scrapes Immoweb for properties based on the provided parameters.
    """
    url = construct_url(
        sort_by=SortBy.NEWEST,
        postal_codes=[9000]
    )

    headers = {"User-Agent": settings.SCRAPER_USER_AGENT}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    properties = []

    # Find all the properties on the page
    property_elements = soup.find_all("li", class_="search-results__item")

    for property_element in property_elements:
        # Extract the property details
        property = Property(
            title=property_element.find("h2", class_="card__title").text.strip(),
            price=property_element.find("span", class_="card__price").text.strip(),
            location=property_element.find("span", class_="card__location").text.strip(),
            link=property_element.find("a", class_="card__title-link")["href"]
        )

        properties.append(property)


get_properties()
