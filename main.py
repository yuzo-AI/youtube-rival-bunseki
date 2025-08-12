#!/usr/bin/env python3
import logging
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import config
from src.storage_handler import StorageHandler
from src.youtube_api import YouTubeAPI
from src.csv_exporter import CSVExporter

logger = config.setup_logging()

class YouTubeAnalyzer:
    """YouTubeチャンネル分析のメイン処理"""
    
    def __init__(self):
        self.storage = StorageHandler()
        self.youtube_api = YouTubeAPI()
        self.csv_exporter = CSVExporter()
    
    def run(self):
        """メイン処理を実行"""
        logger.info("=== YouTube競合チャンネル分析バッチ処理を開始 ===")
        
        try:
            urls = self.storage.read_url_list()
            if not urls:
                logger.warning("処理対象のURLがありません")
                return
            
            logger.info(f"処理対象チャンネル数: {len(urls)}")
            
            success_count = 0
            error_count = 0
            
            for i, url in enumerate(urls, 1):
                logger.info(f"[{i}/{len(urls)}] 処理開始: {url}")
                
                try:
                    self._process_channel(url)
                    success_count += 1
                except Exception as e:
                    logger.error(f"チャンネル処理エラー: {url}, エラー: {e}")
                    error_count += 1
                    continue
            
            logger.info(f"=== 処理完了: 成功 {success_count}件, エラー {error_count}件 ===")
            
        except Exception as e:
            logger.error(f"致命的なエラーが発生しました: {e}")
            raise
    
    def _process_channel(self, url: str):
        """個別のチャンネルを処理"""
        channel_info = self.youtube_api.get_channel_info(url)
        if not channel_info:
            logger.error(f"チャンネル情報を取得できません: {url}")
            return
        
        logger.info(f"チャンネル名: {channel_info['title']}")
        
        video_ids = self.youtube_api.get_all_video_ids(channel_info['uploads_playlist_id'])
        if not video_ids:
            logger.warning(f"動画が見つかりません: {channel_info['title']}")
            return
        
        videos = self.youtube_api.get_videos_details(video_ids)
        if not videos:
            logger.warning(f"ショート動画が見つかりません: {channel_info['title']}")
            return
        
        csv_content = self.csv_exporter.export_channel_data(channel_info, videos)
        
        file_path = self.storage.save_csv(channel_info['title'], csv_content)
        logger.info(f"保存完了: {file_path}")

def main():
    """エントリーポイント"""
    try:
        analyzer = YouTubeAnalyzer()
        analyzer.run()
    except KeyboardInterrupt:
        logger.info("処理が中断されました")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()