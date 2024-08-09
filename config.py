from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET="SECRET"
    DATABASE_URI="sqlite:///site.db"
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USE_SSL=False
    MAIL_USERNAME=os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD')