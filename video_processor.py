import os
import re
import yt_dlp
import logging
import tempfile
from urllib.parse import urlparse
from datetime import datetime

class VideoProcessor:
    def __init__(self):
        self.download_dir = tempfile.mkdtemp()
        self.supported_domains = [
            'youtube.com', 'youtu.be', 'www.youtube.com',
            'instagram.com', 'www.instagram.com',
            'tiktok.com', 'www.tiktok.com',
            'twitter.com', 'www.twitter.com', 'x.com', 'www.x.com'
        ]
        
    def is_valid_url(self, url):
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def is_supported_platform(self, url):
        """Check if the platform is supported"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            return any(supported_domain in domain for supported_domain in self.supported_domains)
        except:
            return False
    
    def get_video_info(self, url):
        """Get video information without downloading"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Extract formats with quality information
                formats = []
                if info and 'formats' in info and info['formats']:
                    for f in info['formats']:
                        # Include both video+audio formats and video-only formats
                        vcodec = f.get('vcodec', 'none')
                        acodec = f.get('acodec', 'none')
                        
                        if vcodec != 'none':  # Has video
                            quality = f.get('format_note', f.get('quality', 'Unknown'))
                            height = f.get('height')
                            fps = f.get('fps')
                            filesize = f.get('filesize')
                            
                            format_desc = quality
                            if height:
                                format_desc = f"{height}p"
                            if fps:
                                format_desc += f" {fps}fps"
                            
                            # Indicate if it has audio
                            if acodec != 'none':
                                format_desc += " (Video + Audio)"
                            else:
                                format_desc += " (Video only)"
                                
                            if filesize:
                                filesize_mb = round(filesize / (1024 * 1024), 1)
                                format_desc += f" - {filesize_mb}MB"
                            
                            formats.append({
                                'format_id': f['format_id'],
                                'description': format_desc,
                                'ext': f.get('ext', 'mp4')
                            })
                
                # Add audio-only formats
                formats.insert(0, {
                    'format_id': 'bestaudio[ext=mp3]/bestaudio',
                    'description': '🎵 Best Audio Quality (MP3)',
                    'ext': 'mp3'
                })
                formats.insert(0, {
                    'format_id': 'bestaudio[ext=m4a]/bestaudio',
                    'description': '🎵 Best Audio Quality (M4A)',
                    'ext': 'm4a'
                })
                
                # Add best quality options with video and audio
                formats.insert(0, {
                    'format_id': 'best[ext=mp4]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
                    'description': '📹 Best MP4 Quality with Audio',
                    'ext': 'mp4'
                })
                formats.insert(0, {
                    'format_id': 'bestvideo+bestaudio/best',
                    'description': '📹 Best Quality Available (Video + Audio)',
                    'ext': 'mp4'
                })
                
                return {
                    'error': None,
                    'title': info.get('title', 'Unknown Title') if info else 'Unknown Title',
                    'duration': self._format_duration(info.get('duration')) if info else 'Unknown',
                    'thumbnail': info.get('thumbnail', '') if info else '',
                    'uploader': info.get('uploader', 'Unknown') if info else 'Unknown',
                    'formats': formats
                }
                
        except Exception as e:
            logging.error(f"Error extracting video info: {str(e)}")
            return {
                'error': f"Could not extract video information: {str(e)}",
                'title': None,
                'duration': None,
                'thumbnail': None,
                'uploader': None,
                'formats': []
            }
    
    def download_video(self, url, format_id='bestvideo+bestaudio/best'):
        """Download video with specified format"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_template = os.path.join(self.download_dir, f"{timestamp}_%(title)s.%(ext)s")
            
            # Use default format that includes audio if no specific format provided
            if format_id == 'best':
                format_id = 'bestvideo+bestaudio/best'
            
            # Determine if this is an audio-only format
            is_audio_only = 'bestaudio' in format_id and 'bestvideo' not in format_id
            
            ydl_opts = {
                'outtmpl': output_template,
                'format': format_id,
                'quiet': True,
                'no_warnings': True,
                'writeinfojson': False,
                'writeautomaticsub': False,
                'writesubtitles': False,
            }
            
            # Only set merge_output_format for video formats
            if not is_audio_only:
                ydl_opts['merge_output_format'] = 'mp4'
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first to get filename
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'video') if info else 'video'
                
                # Clean title for filename
                clean_title = re.sub(r'[^\w\s-]', '', title)
                clean_title = re.sub(r'[-\s]+', '-', clean_title)
                
                # Download the video
                ydl.download([url])
                
                # Find the downloaded file
                for file in os.listdir(self.download_dir):
                    if file.startswith(timestamp):
                        filepath = os.path.join(self.download_dir, file)
                        return {
                            'error': None,
                            'filepath': filepath,
                            'filename': f"{clean_title}.{file.split('.')[-1]}"
                        }
                
                return {
                    'error': 'Downloaded file not found',
                    'filepath': None,
                    'filename': None
                }
                
        except Exception as e:
            logging.error(f"Error downloading video: {str(e)}")
            return {
                'error': f"Download failed: {str(e)}",
                'filepath': None,
                'filename': None
            }
    
    def _format_duration(self, duration):
        """Format duration in seconds to readable format"""
        if not duration:
            return "Unknown"
        
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        seconds = duration % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
