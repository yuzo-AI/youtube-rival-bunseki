import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.csv_exporter import CSVExporter

class TestCSVExporter:
    
    def test_export_channel_data(self):
        exporter = CSVExporter()
        
        channel_info = {
            'title': 'Test Channel',
            'description': 'Test Description',
            'published_at': '2023-01-01T00:00:00Z'
        }
        
        videos = [
            {
                'title': 'Test Video 1',
                'url': 'https://youtube.com/watch?v=test1',
                'published_at': '2023-06-01T00:00:00Z',
                'view_count': 1000,
                'like_count': 100,
                'comment_count': 10,
                'duration_seconds': 30,
                'thumbnail_url': 'https://example.com/thumb1.jpg',
                'tags': 'tag1,tag2'
            }
        ]
        
        csv_content = exporter.export_channel_data(channel_info, videos)
        
        assert 'チャンネル名' in csv_content
        assert 'Test Channel' in csv_content
        assert 'Test Video 1' in csv_content
        assert '1000' in csv_content
    
    def test_format_date(self):
        exporter = CSVExporter()
        
        assert exporter._format_date('2023-01-01T12:34:56Z') == '2023-01-01'
        assert exporter._format_date('') == ''
        assert exporter._format_date('invalid') == 'invalid'