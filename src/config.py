import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """アプリケーション設定"""
    
    def __init__(self):
        self.LOCAL_MODE = os.getenv("LOCAL_MODE", "True").lower() == "true"
        self.YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
        
        if not self.LOCAL_MODE:
            self.GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
            self.GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
            self.SECRET_NAME = os.getenv("SECRET_NAME", "youtube-api-key")
        
        if self.LOCAL_MODE:
            self.LOCAL_INPUT_PATH = Path(os.getenv("LOCAL_INPUT_PATH", "./input/url_list.txt"))
            self.LOCAL_OUTPUT_PATH = Path(os.getenv("LOCAL_OUTPUT_PATH", "./output/"))
            self.LOCAL_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
            
            input_dir = self.LOCAL_INPUT_PATH.parent
            input_dir.mkdir(parents=True, exist_ok=True)
    
    def get_youtube_api_key(self) -> Optional[str]:
        """YouTube APIキーを取得"""
        if self.LOCAL_MODE:
            return self.YOUTUBE_API_KEY
        else:
            from google.cloud import secretmanager
            client = secretmanager.SecretManagerServiceClient()
            name = f"projects/{self.GCP_PROJECT_ID}/secrets/{self.SECRET_NAME}/versions/latest"
            response = client.access_secret_version(request={"name": name})
            return response.payload.data.decode("UTF-8")
    
    def setup_logging(self) -> logging.Logger:
        """ロギング設定"""
        if self.LOCAL_MODE:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler('youtube_analysis.log')
                ]
            )
            return logging.getLogger(__name__)
        else:
            from google.cloud import logging as cloud_logging
            client = cloud_logging.Client()
            client.setup_logging()
            return logging.getLogger(__name__)

config = Config()