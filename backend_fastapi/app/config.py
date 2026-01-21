"""
FastAPI Configuration using Pydantic Settings
Replaces Django's settings.py with type-safe configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # PostgreSQL Database Configuration
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "invoice_generator"
    postgres_user: str = "invoice_user"
    postgres_password: str = ""

    @property
    def database_url(self) -> str:
        """Construct PostgreSQL async database URL"""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # AWS SES Configuration
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-east-1"
    ses_sender_email: str = ""
    email_from_name: str = "Invoice Generator"

    # Twilio Configuration (WhatsApp)
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_from: str = "whatsapp:+14155238886"

    # SuprSend Configuration
    suprsend_workspace_key: str = ""
    suprsend_workspace_secret: str = ""
    suprsend_workspace_url: str = "https://hub.suprsend.com"
    suprsend_invoice_template: str = "follower-testimonial-request-free-calls"

    # Topmate Invoice Settings
    topmate_company_name: str = "Topmate Technologies Pvt Ltd"
    topmate_gstin: str = "29AAFCT0123A1Z5"
    topmate_address: str = "123 Business Park, HSR Layout, Bangalore, Karnataka"
    topmate_pincode: str = "560102"
    topmate_state: str = "Karnataka"
    topmate_state_code: str = "29"
    topmate_phone: str = "+91 8012345678"
    topmate_email: str = "invoices@topmate.io"
    topmate_website: str = "https://topmate.io"
    topmate_invoice_prefix: str = "TM-INV"
    user_invoice_prefix: str = "USER"

    # GST Settings (percentages)
    gst_rate: float = 18.0
    cgst_rate: float = 9.0
    sgst_rate: float = 9.0
    igst_rate: float = 18.0

    # CORS Settings
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002",
    ]
    cors_allow_credentials: bool = True

    # Media Storage
    media_root: str = "./media"
    media_url: str = "/media/"

    # Pagination
    page_size: int = 20

    # Timezone
    timezone: str = "Asia/Kolkata"

    # Debug Mode
    debug: bool = True


# Create singleton settings instance
settings = Settings()


# For backwards compatibility and easy import
def get_settings() -> Settings:
    """Get settings instance"""
    return settings
