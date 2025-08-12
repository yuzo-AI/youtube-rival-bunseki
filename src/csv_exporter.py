import csv
import io
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class CSVExporter:
    """CSV出力を管理"""
    
    def __init__(self):
        self.headers = [
            '動画タイトル',
            '動画URL',
            'アップロード日',
            '再生回数',
            '高評価数',
            'コメント数',
            '動画の長さ(秒)',
            'サムネイル画像URL',
            '動画タグ',
            'チャンネル名',
            'チャンネル開始日'
        ]
    
    def export_channel_data(self, channel_info: Dict[str, Any], videos: List[Dict[str, Any]]) -> str:
        """チャンネルデータをCSV形式で出力"""
        output = io.StringIO()
        writer = csv.writer(output, lineterminator='\n')
        
        writer.writerow(self.headers)
        
        for video in videos:
            row = [
                video.get('title', ''),
                video.get('url', ''),
                self._format_date(video.get('published_at', '')),
                video.get('view_count', 0),
                video.get('like_count', 0),
                video.get('comment_count', 0),
                video.get('duration_seconds', 0),
                video.get('thumbnail_url', ''),
                video.get('tags', ''),
                channel_info.get('title', ''),
                self._format_date(channel_info.get('published_at', ''))
            ]
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        logger.info(f"CSVデータを生成しました: {channel_info.get('title', 'Unknown')} - {len(videos)}件の動画")
        return csv_content
    
    def _format_date(self, date_str: str) -> str:
        """日付をYYYY-MM-DD形式にフォーマット"""
        if not date_str:
            return ''
        
        try:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')
        except Exception:
            return date_str