from enums.enums import SortBy, TypeOfTransaction, PropertyType, PriceType
from model.property import Property
from settings.application_settings import settings
from typing import Optional, List, Union, Dict, Any
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
from dataclasses import dataclass


@dataclass
class FilterOptions:
    """
    Dataclass to hold all filter options for property search.
    Makes it easy to customize and reuse filter combinations.
    """
    property_types: Union[PropertyType, List[PropertyType]] = None
    type_of_transaction: TypeOfTransaction = None
    countries: str = "BE"
    immediately_available: Optional[bool] = None
    min_bedrooms: Optional[int] = None
    max_bedrooms: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    cities: Optional[List[str]] = None
    postal_codes: Optional[List[int]] = None
    sort_by: SortBy = SortBy.NEWEST

    def to_dict(self) -> Dict[str, Any]:
        """Convert options to a dictionary, excluding None values"""
        return {k: v for k, v in self.__dict__.items() if v is not None}


def extract_attribute(driver, selector, attribute, wait_time=5, default=None):
    """Helper method to extract attribute with proper error handling"""
    try:
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element.get_attribute(attribute)
    except (TimeoutException, NoSuchElementException):
        return default


def extract_text(driver, selector, wait_time=5, default=None):
    """Helper method to extract text with proper error handling"""
    try:
        element = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element.text
    except (TimeoutException, NoSuchElementException):
        return default


class ImmowebScraper:
    """
    Enhanced scraper for Immoweb properties with flexible filtering options.
    """

    def __init__(self, headless: bool = True, user_agent: str = settings.SCRAPER_USER_AGENT):
        self.headless = headless
        self.user_agent = user_agent

    def setup_driver(self):
        """
        Set up and return a configured Chrome WebDriver instance.
        """
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={self.user_agent}")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        return driver

    def construct_url(self, filter_options: FilterOptions) -> str:
        """
        Constructs a URL for Immoweb based on the provided FilterOptions.
        """
        base_url = settings.IMMOWEB_BASE_URL

        # Validate required parameters
        if not filter_options.property_types:
            filter_options.property_types = settings.PROPERTY_TYPES
        if not filter_options.type_of_transaction:
            filter_options.type_of_transaction = settings.TYPE_OF_TRANSACTION
        if not filter_options.postal_codes and not filter_options.cities:
            raise ValueError("At least one postal code or city is required.")

        # Build base URL path
        url = f"{base_url}/{filter_options.property_types}/{filter_options.type_of_transaction.value}"

        # Build query parameters
        query_params = []

        # Add basic filters
        if filter_options.countries:
            query_params.append(f"countries={filter_options.countries}")

        if filter_options.immediately_available is not None:
            query_params.append(f"isImmediatelyAvailable={str(filter_options.immediately_available).lower()}")

        if filter_options.min_bedrooms is not None:
            query_params.append(f"minBedroomCount={filter_options.min_bedrooms}")
        if filter_options.max_bedrooms is not None:
            query_params.append(f"maxBedroomCount={filter_options.max_bedrooms}")

        if filter_options.min_price is not None:
            query_params.append(f"minPrice={filter_options.min_price}")
        if filter_options.max_price is not None:
            query_params.append(f"maxPrice={filter_options.max_price}")

        # Add price type based on transaction type
        if filter_options.type_of_transaction == TypeOfTransaction.RENT:
            query_params.append(f"priceType={PriceType.MONTHLY.value}")
        elif filter_options.type_of_transaction == TypeOfTransaction.SALE:
            query_params.append(f"priceType={PriceType.SALE.value}")

        # Add location filters
        if filter_options.cities:
            query_params.append(f"cities={','.join(filter_options.cities)}")

        if filter_options.postal_codes:
            query_params.append(f"postalCodes={','.join(map(str, filter_options.postal_codes))}")

        # Add sorting parameter
        query_params.append(f"orderBy={filter_options.sort_by.value}")

        # Combine everything
        if query_params:
            url += "?" + "&".join(query_params)

        return url

    def get_properties(self, filter_options: Optional[FilterOptions] = None, max_properties: int = 20) -> list[str]:
        """
        Scrapes Immoweb for properties using Selenium with custom filters.
        Returns a list of property links.
        """
        if filter_options is None:
            filter_options = FilterOptions(
                postal_codes=[9000],  # Default to Ghent
                sort_by=SortBy.NEWEST
            )

        url = self.construct_url(filter_options)
        print(f"Searching with URL: {url}")

        driver = self.setup_driver()
        try:
            driver.get(url)
            sleep(3)  # Allow page to load

            properties = []
            try:
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

                print(f"Found {len(properties)} properties")
            except TimeoutException:
                print("No properties found with the current filters")

            return properties
        finally:
            driver.quit()

    def get_property_details(self, property_link: str) -> Property:
        """
        Fetches and extracts property details from a given property link using Selenium.
        Returns a Property object with all available details.
        """
        driver = self.setup_driver()
        try:
            driver.get(property_link)
            wait = WebDriverWait(driver, 10)

            # Extract basic info
            price = extract_text(driver, ".classified__price span")
            address = extract_text(driver, "iw-classified-address")

            # Try alternative address selector if the first one fails
            if not address:
                address = extract_text(driver, ".classified__information--address")

            # Extract transaction type from title
            title = extract_text(driver, ".classified__title")
            transaction_type = None
            if title:
                title_lower = title.lower()
                if "for sale" in title_lower:
                    transaction_type = TypeOfTransaction.SALE
                elif "for rent" in title_lower:
                    transaction_type = TypeOfTransaction.RENT

            return Property(
                price=price,
                locality=address,
                type_of_transaction=transaction_type,
                link=property_link,
            )
        finally:
            driver.quit()

    def scrape_all_properties(self, filter_options: Optional[FilterOptions] = None,
                              max_properties: int = 10) -> list[Property]:
        """
        Scrapes multiple properties with the given filters and returns a list of Property objects.
        """
        property_links = self.get_properties(filter_options, max_properties)
        all_properties = []

        for i, link in enumerate(property_links):
            try:
                print(f"Scraping property {i + 1}/{len(property_links)}: {link}")
                property_obj = self.get_property_details(link)
                all_properties.append(property_obj)

                # Add a small delay between requests to avoid overloading the server
                sleep(1)
            except Exception as e:
                print(f"Error scraping property {link}: {str(e)}")

        return all_properties