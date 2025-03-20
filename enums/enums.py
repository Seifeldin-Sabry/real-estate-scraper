from enum import Enum


class PropertyType(Enum):
    APARTMENT = 'apartment'
    HOUSE = 'house'
    HOUSE_APARTMENT = 'house-and-apartment'
    GARAGE = 'garage'
    OFFICE = 'office'
    BUSINESS = 'business'
    INDUSTRY = 'industry'
    LAND = 'land'
    OTHER = 'other'


class TypeOfTransaction(Enum):
    RENT = 'for-rent'
    SALE = 'for-sale'


class PriceType(Enum):
    MONTHLY = 'MONTHLY_RENTAL_PRICE'
    SALE = 'SALE_PRICE'


class SortBy(Enum):
    RELEVANCE = 'relevance'
    PRICE_ASC = 'cheapest'
    PRICE_DESC = 'most-expensive'
    NEWEST = 'newest'
    POSTAL_CODE = 'postal-code'
