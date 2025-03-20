from db.property import get_latest_properties, add_properties, delete_properties
from enums.enums import PropertyType, TypeOfTransaction, SortBy
from messaging.telegram_bot import send_message
from scrape.scraper import ImmowebScraper, FilterOptions

if __name__ == '__main__':
    list_props = get_latest_properties()
    scraper = ImmowebScraper(headless=True)
    detailed_filters = FilterOptions(
        property_types=[PropertyType.HOUSE_APARTMENT],
        type_of_transaction=TypeOfTransaction.RENT,
        cities=["Antwerp"],
        postal_codes=[2000, 2018, 2020, 2030, 2050],
        min_price=750,
        max_price=2000,
        min_bedrooms=1,
        max_bedrooms=3,
        sort_by=SortBy.NEWEST
    )
    max_properties = 5

    if len(list_props) == 0:

        properties = scraper.scrape_all_properties(
            filter_options=detailed_filters,
            max_properties=max_properties
        )

        print("Added properties to the Database.")
        send_message(message=f"""
            Initial properties added to the Database:
            {"\n".join([str(prop) for prop in properties])}
            """)
        add_properties(properties)
        exit(0)

    print("Comparing latest properties with Immoweb...")
    properties = scraper.scrape_all_properties(
        filter_options=detailed_filters,
        max_properties=max_properties
    )

    new_properties = []
    old_properties = []

    for prop in properties:
        if prop not in list_props:
            new_properties.append(prop)
        else:
            old_properties.append(prop)

    if new_properties:
        send_message(message=f"""
                New properties found:
                {"\n".join([str(prop) for prop in new_properties])}
                """)
        add_properties(new_properties)
        delete_properties(old_properties)
        print("Added new properties to the Database.")
        print("Deleted old properties from the Database.")
    else:
        print("No new properties found.")

