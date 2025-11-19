from dotenv import load_dotenv
import os


load_dotenv()

class Settings:
    PROJECT_NAME: str = "JurisGPT Backend"
    ENV: str = os.getenv("ENV", "dev")

settings = Settings()
