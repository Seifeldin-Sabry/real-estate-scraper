from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv
from enums.enums import PropertyType, TypeOfTransaction, PriceType

load_dotenv()


class Settings(BaseSettings):
    SCRAPER_USER_AGENT: str = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                               "Chrome/91.0.4472.124 Safari/537.36")
    SCRAPER_RATE_LIMIT_DELAY: float = 2.0

    TELEGRAM_BOT_TOKEN: str = Field()
    TELEGRAM_CHAT_ID: str = Field()

    IMMOWEB_BASE_URL: str = "https://www.immoweb.be/en/search"
    PROPERTY_TYPES: PropertyType = PropertyType.HOUSE_APARTMENT
    TYPE_OF_TRANSACTION: TypeOfTransaction = TypeOfTransaction.RENT

    model_config = SettingsConfigDict()


settings = Settings()
