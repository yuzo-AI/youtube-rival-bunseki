import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.youtube_api import YouTubeAPI

class TestYouTubeAPI:
    
    @patch('src.youtube_api.config.get_youtube_api_key')
    @patch('src.youtube_api.build')
    def test_init_with_valid_key(self, mock_build, mock_get_key):
        mock_get_key.return_value = "test_api_key"
        api = YouTubeAPI()
        assert api.youtube is not None
        mock_build.assert_called_once_with('youtube', 'v3', developerKey='test_api_key')
    
    @patch('src.youtube_api.config.get_youtube_api_key')
    def test_init_without_key(self, mock_get_key):
        mock_get_key.return_value = None
        with pytest.raises(ValueError, match="YouTube APIキーが設定されていません"):
            YouTubeAPI()
    
    @patch('src.youtube_api.config.get_youtube_api_key')
    @patch('src.youtube_api.build')
    def test_extract_channel_id_from_channel_url(self, mock_build, mock_get_key):
        mock_get_key.return_value = "test_api_key"
        api = YouTubeAPI()
        
        channel_id = api._extract_channel_id("https://www.youtube.com/channel/UC1234567890")
        assert channel_id == "UC1234567890"
    
    @patch('src.youtube_api.config.get_youtube_api_key')
    @patch('src.youtube_api.build')
    def test_is_short_video(self, mock_build, mock_get_key):
        mock_get_key.return_value = "test_api_key"
        api = YouTubeAPI()
        
        assert api._is_short_video({'duration_seconds': 30}) == True
        assert api._is_short_video({'duration_seconds': 60}) == True
        assert api._is_short_video({'duration_seconds': 61}) == False
        assert api._is_short_video({'duration_seconds': 120}) == False
    
    @patch('src.youtube_api.config.get_youtube_api_key')
    @patch('src.youtube_api.build')
    def test_sanitize_filename(self, mock_build, mock_get_key):
        mock_get_key.return_value = "test_api_key"
        api = YouTubeAPI()
        
        from src.storage_handler import StorageHandler
        handler = StorageHandler()
        
        assert handler._sanitize_filename("test/file") == "test／file"
        assert handler._sanitize_filename("test:file") == "test：file"
        assert handler._sanitize_filename("test<>file") == "test＜＞file"