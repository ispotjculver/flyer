import os

class Config:
    # Survey API configuration
    SURVEY_API_BASE_URL = os.getenv('SURVEY_API_BASE_URL', 'https://survey-int.acemetrix.com')
    
    # AWS S3 configuration
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    S3_BUCKET = os.getenv('S3_BUCKET', 'survey-replay-data')