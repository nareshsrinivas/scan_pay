from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 30
    
    # QR Code
    QR_SECRET: str
    QR_EXPIRY_MINUTES: int = 10
    
    # Payment Mode: "demo" or "razorpay"
    PAYMENT_MODE: str = "demo"
    
    # Demo Payment Settings
    DEMO_PAYMENT_DELAY_SECONDS: int = 3
    DEMO_FAILURE_RATE: int = 0  # 0-100 percentage
    
    # Razorpay Settings
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""
    
    # Legacy payment keys (for backward compatibility)
    PAYMENT_KEY: str = ""
    PAYMENT_SECRET: str = ""
    PAYMENT_WEBHOOK_SECRET: str = ""
    
    # n8n
    N8N_WEBHOOK_URL: str = ""
    N8N_ENABLED: bool = True
    
    # AI Service
    AI_SERVICE_ENABLED: bool = False
    AI_SERVICE_URL: str = "http://localhost:8001"
    
    # App
    APP_NAME: str = "Smart Checkout System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

def get_settings():
    return settings
