import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from src.config import config

logger = logging.getLogger(__name__)

class StorageHandler:
    """ファイルストレージの操作を管理"""
    
    def __init__(self):
        self.local_mode = config.LOCAL_MODE
        if not self.local_mode:
            from google.cloud import storage
            self.storage_client = storage.Client()
            self.bucket = self.storage_client.bucket(config.GCS_BUCKET_NAME)
    
    def read_url_list(self) -> List[str]:
        """url_list.txtを読み込んでURLリストを返す"""
        if self.local_mode:
            file_path = config.LOCAL_INPUT_PATH
            if not file_path.exists():
                logger.error(f"入力ファイルが見つかりません: {file_path}")
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            blob = self.bucket.blob("input/url_list.txt")
            if not blob.exists():
                logger.error("入力ファイルが見つかりません: input/url_list.txt")
                raise FileNotFoundError("File not found: input/url_list.txt")
            content = blob.download_as_text()
        
        urls = []
        for line in content.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if self._validate_youtube_url(line):
                    urls.append(line)
                else:
                    logger.warning(f"無効なURLをスキップ: {line}")
        
        if not urls:
            logger.warning("有効なURLが見つかりませんでした")
        
        return urls
    
    def _validate_youtube_url(self, url: str) -> bool:
        """YouTube URLの妥当性を検証（チャンネルURL、動画URLの両方に対応）"""
        valid_patterns = [
            'youtube.com/channel/',
            'youtube.com/@',
            'youtube.com/c/',
            'youtube.com/user/',
            'youtube.com/watch?v=',  # 動画URLも受け入れる
            'youtu.be/'  # 短縮URLも受け入れる
        ]
        return any(pattern in url for pattern in valid_patterns)
    
    def save_csv(self, channel_name: str, csv_content: str) -> str:
        """CSVファイルを保存"""
        date_str = datetime.now().strftime('%Y%m%d')
        safe_channel_name = self._sanitize_filename(channel_name)
        filename = f"{safe_channel_name}_{date_str}.csv"
        
        if self.local_mode:
            output_dir = config.LOCAL_OUTPUT_PATH / date_str
            output_dir.mkdir(parents=True, exist_ok=True)
            file_path = output_dir / filename
            
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(csv_content)
            
            logger.info(f"CSVファイルを保存しました: {file_path}")
            return str(file_path)
        else:
            blob_path = f"output/{date_str}/{filename}"
            blob = self.bucket.blob(blob_path)
            blob.upload_from_string(csv_content.encode('utf-8-sig'))
            
            logger.info(f"CSVファイルを保存しました: gs://{config.GCS_BUCKET_NAME}/{blob_path}")
            return f"gs://{config.GCS_BUCKET_NAME}/{blob_path}"
    
    def _sanitize_filename(self, filename: str) -> str:
        """ファイル名として使用できない文字を置換"""
        invalid_chars = {
            '/': '／', '\\': '￥', ':': '：', '*': '＊',
            '?': '？', '"': '"', '<': '＜', '>': '＞', '|': '｜'
        }
        for char, replacement in invalid_chars.items():
            filename = filename.replace(char, replacement)
        return filename