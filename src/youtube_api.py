import logging
import time
import re
from typing import List, Dict, Optional, Any
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate
from src.config import config

logger = logging.getLogger(__name__)

class YouTubeAPI:
    """YouTube Data APIの操作を管理"""
    
    def __init__(self):
        api_key = config.get_youtube_api_key()
        if not api_key:
            raise ValueError("YouTube APIキーが設定されていません")
        
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.max_retries = 3
        self.retry_delay = 1
    
    def get_channel_info(self, channel_url: str) -> Optional[Dict[str, Any]]:
        """チャンネル情報を取得（動画URLからも対応）"""
        # 動画URLの場合、まず動画情報からチャンネルIDを取得
        if 'watch?v=' in channel_url or 'youtu.be/' in channel_url:
            channel_id = self._get_channel_id_from_video_url(channel_url)
        else:
            channel_id = self._extract_channel_id(channel_url)
        
        if not channel_id:
            logger.error(f"チャンネルIDを抽出できません: {channel_url}")
            return None
        
        try:
            response = self._api_call_with_retry(
                self.youtube.channels().list(
                    part='snippet,contentDetails',
                    id=channel_id
                )
            )
            
            if not response or not response.get('items'):
                logger.warning(f"チャンネルが見つかりません: {channel_url}")
                return None
            
            channel = response['items'][0]
            return {
                'id': channel['id'],
                'title': channel['snippet'].get('title', ''),
                'description': channel['snippet'].get('description', ''),
                'published_at': channel['snippet'].get('publishedAt', ''),
                'uploads_playlist_id': channel['contentDetails']['relatedPlaylists']['uploads']
            }
        except Exception as e:
            logger.error(f"チャンネル情報の取得に失敗: {channel_url}, エラー: {e}")
            return None
    
    def get_all_video_ids(self, playlist_id: str) -> List[str]:
        """プレイリストから全動画IDを取得"""
        video_ids = []
        next_page_token = None
        page_count = 0
        
        while True:
            try:
                response = self._api_call_with_retry(
                    self.youtube.playlistItems().list(
                        part='contentDetails',
                        playlistId=playlist_id,
                        maxResults=50,
                        pageToken=next_page_token
                    )
                )
                
                if not response:
                    break
                
                page_count += 1
                items = response.get('items', [])
                logger.debug(f"ページ {page_count}: {len(items)}件の動画を取得")
                
                for item in items:
                    video_ids.append(item['contentDetails']['videoId'])
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                    
            except Exception as e:
                logger.error(f"動画リストの取得に失敗: {e}")
                break
        
        logger.info(f"取得した動画数: {len(video_ids)}")
        return video_ids
    
    def get_videos_details(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """動画の詳細情報を取得（50件ずつバッチ処理）"""
        videos = []
        
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            
            try:
                response = self._api_call_with_retry(
                    self.youtube.videos().list(
                        part='snippet,contentDetails,statistics',
                        id=','.join(batch_ids)
                    )
                )
                
                if not response:
                    continue
                
                for item in response.get('items', []):
                    video_data = self._parse_video_data(item)
                    if video_data and self._is_short_video(video_data):
                        videos.append(video_data)
                        
            except Exception as e:
                logger.error(f"動画詳細の取得に失敗: {e}")
                continue
        
        logger.info(f"ショート動画数: {len(videos)}")
        return videos
    
    def _parse_video_data(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """動画データをパース"""
        try:
            duration = item['contentDetails'].get('duration', 'PT0S')
            duration_seconds = int(isodate.parse_duration(duration).total_seconds())
            
            return {
                'id': item['id'],
                'title': item['snippet'].get('title', ''),
                'published_at': item['snippet'].get('publishedAt', ''),
                'duration_seconds': duration_seconds,
                'view_count': int(item['statistics'].get('viewCount', 0)),
                'like_count': int(item['statistics'].get('likeCount', 0)),
                'comment_count': int(item['statistics'].get('commentCount', 0)),
                'thumbnail_url': item['snippet'].get('thumbnails', {}).get('high', {}).get('url', ''),
                'tags': ','.join(item['snippet'].get('tags', [])),
                'url': f"https://www.youtube.com/watch?v={item['id']}"
            }
        except Exception as e:
            logger.warning(f"動画データのパースに失敗: {item.get('id', 'unknown')}, エラー: {e}")
            return None
    
    def _is_short_video(self, video_data: Dict[str, Any]) -> bool:
        """ショート動画かどうかを判定"""
        return video_data['duration_seconds'] <= 61
    
    def _get_channel_id_from_video_url(self, url: str) -> Optional[str]:
        """動画URLからチャンネルIDを取得"""
        video_id = None
        
        # 動画IDを抽出
        if 'watch?v=' in url:
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            video_id = params.get('v', [None])[0]
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0]
        
        if not video_id:
            return None
        
        try:
            # 動画情報からチャンネルIDを取得
            response = self._api_call_with_retry(
                self.youtube.videos().list(
                    part='snippet',
                    id=video_id
                )
            )
            
            if response and response.get('items'):
                return response['items'][0]['snippet']['channelId']
        except Exception as e:
            logger.error(f"動画からチャンネルID取得に失敗: {e}")
        
        return None
    
    def _extract_channel_id(self, url: str) -> Optional[str]:
        """URLからチャンネルIDを抽出"""
        import urllib.parse
        
        # URLデコード
        url = urllib.parse.unquote(url)
        
        patterns = [
            r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
            r'youtube\.com/@([^/\?]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                channel_identifier = match.group(1)
                
                if '@' in url:
                    try:
                        # まずハンドル名で検索
                        response = self._api_call_with_retry(
                            self.youtube.search().list(
                                part='id,snippet',
                                q=channel_identifier,
                                type='channel',
                                maxResults=1
                            )
                        )
                        if response and response.get('items'):
                            # ハンドル名が一致するか確認
                            for item in response['items']:
                                custom_url = item.get('snippet', {}).get('customUrl', '')
                                if custom_url and channel_identifier.lower() in custom_url.lower():
                                    return item['id']['channelId']
                            # 一致しない場合でも最初の結果を返す
                            return response['items'][0]['id']['channelId']
                    except Exception as e:
                        logger.error(f"チャンネルIDの取得に失敗: {e}")
                        return None
                else:
                    return channel_identifier
        
        return None
    
    def _api_call_with_retry(self, request):
        """APIコールをリトライ機能付きで実行"""
        for attempt in range(self.max_retries):
            try:
                return request.execute()
            except HttpError as e:
                if e.resp.status == 403 and 'quotaExceeded' in str(e):
                    logger.error("APIクォータが超過しました")
                    raise
                elif e.resp.status in [429, 500, 502, 503, 504]:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)
                        logger.warning(f"APIエラー {e.resp.status}. {wait_time}秒後にリトライします...")
                        time.sleep(wait_time)
                        continue
                logger.error(f"APIエラー: {e}")
                raise
            except Exception as e:
                logger.error(f"予期しないエラー: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise
        
        return None