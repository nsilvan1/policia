# /policia_civil/config.py
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb+srv://nsnunes01:1pNO2JJzZTotwsmB@cluster0.tqvnk7i.mongodb.net/policia_civil')
