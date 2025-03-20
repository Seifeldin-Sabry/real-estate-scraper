from enums.enums import PropertyType, TypeOfTransaction, PriceType, SortBy
from settings.application_settings import settings

from typing import Optional


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
        query_params.append(f"cities={",".join(cities)}")

    if postal_codes:
        query_params.append(f"postalCodes={','.join(map(str, postal_codes))}")

    query_params.append(f"orderBy={sort_by.value}")

    if query_params:
        url += "?" + "&".join(query_params)

    return url
