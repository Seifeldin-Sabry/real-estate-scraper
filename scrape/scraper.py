from enums.enums import SortBy, TypeOfTransaction, PropertyType, PriceType
from model.property import Property
from settings.application_settings import settings
from typing import Optional, List
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep


def construct_url(
        base_url: str = settings.IMMOWEB_BASE_URL,
        property_types: PropertyType = settings.PROPERTY_TYPES,
        type_of_transaction: TypeOfTransaction = settings.TYPE_OF_TRANSACTION,
        countries: Optional[str] = "BE",
        immediately_available: Optional[bool] = None,
        min_bedrooms: Optional[int] = None,
        max_bedrooms: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        cities: list[str] = None,
        postal_codes: list[int] = None,
        sort_by: Optional[SortBy] = SortBy.RELEVANCE
) -> str:
    """
    Constructs a URL for Immoweb based on the provided parameters.
    """
    # Start with the base URL
    if not base_url:
        raise ValueError("Base URL is required.")
    if not property_types:
        raise ValueError("Property type is required.")
    if not type_of_transaction:
        raise ValueError("Type of transaction is required.")
    if not postal_codes and not cities:
        raise ValueError("At least one postal code or city is required.")

    url = base_url

    if property_types:
        url += f"/{property_types.value}"

    if type_of_transaction:
        url += f"/{type_of_transaction.value}"

    query_params = []

    if countries:
        query_params.append(f"countries={countries}")

    if immediately_available is not None:
        query_params.append(f"isImmediatelyAvailable={str(immediately_available).lower()}")

    if min_bedrooms is not None:
        query_params.append(f"minBedroomCount={min_bedrooms}")
    if max_bedrooms is not None:
        query_params.append(f"maxBedroomCount={max_bedrooms}")

    if min_price is not None:
        query_params.append(f"minPrice={min_price}")
    if max_price is not None:
        query_params.append(f"maxPrice={max_price}")

    if type_of_transaction == TypeOfTransaction.RENT:
        query_params.append(f"priceType={PriceType.MONTHLY.value}")
    elif type_of_transaction == TypeOfTransaction.SALE:
        query_params.append(f"priceType={PriceType.SALE.value}")

    if cities:
        query_params.append(f"cities={','.join(cities)}")

    if postal_codes:
        query_params.append(f"postalCodes={','.join(map(str, postal_codes))}")

    query_params.append(f"orderBy={sort_by.value}")

    if query_params:
        url += "?" + "&".join(query_params)

    return url


def setup_driver():
    """
    Set up and return a configured Chrome WebDriver instance.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={settings.SCRAPER_USER_AGENT}")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def get_properties(
        property_types: PropertyType = settings.PROPERTY_TYPES,
        type_of_transaction: TypeOfTransaction = settings.TYPE_OF_TRANSACTION,
        postal_codes: list[int] = None,
        cities: list[str] = None,
        sort_by: SortBy = SortBy.NEWEST,
        max_properties: int = 20
) -> list[str]:
    """
    Scrapes Immoweb for properties using Selenium.
    Returns a list of property links.
    """
    if postal_codes is None and cities is None:
        postal_codes = [9000]  # Default to Ghent

    url = construct_url(
        property_types=property_types,
        type_of_transaction=type_of_transaction,
        postal_codes=postal_codes,
        cities=cities,
        sort_by=sort_by
    )

    driver = setup_driver()
    try:
        driver.get(url)
        sleep(3)  # Allow page to load

        properties = []
        # Wait for property cards to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article.card--result"))
        )

        # Find all property cards
        property_elements = driver.find_elements(By.CSS_SELECTOR, "article.card--result")

        for property_element in property_elements[:max_properties]:
            try:
                # Find the link within the property card
                property_link = property_element.find_element(By.TAG_NAME, "a").get_attribute("href")
                if property_link:
                    properties.append(property_link)
            except NoSuchElementException:
                continue

        return properties
    finally:
        driver.quit()


def get_property_details(property_link: str) -> Property:
    """
    Fetches and extracts property details from a given property link using Selenium.
    """
    driver = setup_driver()
    try:
        driver.get(property_link)

        # Wait for page to load fully
        wait = WebDriverWait(driver, 10)

        price = None
        address = None
        transaction_type = None

        try:
            price_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".classified__price span"))
            )
            price_text = price_element.text
            price = price_text
        except (TimeoutException, NoSuchElementException):
            price = None

        try:
            address_element = wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "iw-classified-address"))
            )
            address = address_element.text
        except (TimeoutException, NoSuchElementException):
            try:
                address_element = driver.find_element(By.CSS_SELECTOR, ".classified__information--address")
                address = address_element.text
            except NoSuchElementException:
                address = None

        # Property type extraction
        try:
            title_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".classified__title"))
            )
            title_text = title_element.text.lower()

            if "for sale" in title_text:
                transaction_type = TypeOfTransaction.SALE
            elif "for rent" in title_text:
                transaction_type = TypeOfTransaction.RENT
            else:
                transaction_type = None

        except (TimeoutException, NoSuchElementException):
            transaction_type = None

        return Property(price=price, locality=address, type_of_transaction=transaction_type, link=property_link)
    finally:
        driver.quit()


def scrape_all_properties(max_properties: int = 10) -> list[Property]:
    """
    Scrapes multiple properties and returns a list of property details.
    """
    property_links = get_properties(max_properties=max_properties)
    all_properties = []

    for link in property_links:
        try:
            pro = get_property_details(link)
            all_properties.append(pro)

            # Add a small delay between requests to avoid overloading the server
            sleep(1)
        except Exception as e:
            print(f"Error scraping property {link}: {str(e)}")

    return all_properties


# Example usage
if __name__ == "__main__":
    # Example 1: Get and print details for a specific property
    property_data = get_property_details("https://www.immoweb.be/en/classified/mansion/for-rent/gent/9000/20601918")
    print("Property Details:")
    print(property_data)

    # Example 2: Scrape multiple properties
    print("\nScraping multiple properties...")
    properties = scrape_all_properties(max_properties=5)
    print(f"Scraped {len(properties)} properties")