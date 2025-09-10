import os
import json
import logging
from flask import render_template, request, jsonify, send_file, flash, redirect, url_for
from app import app
from video_processor import VideoProcessor
from urllib.parse import urlparse

video_processor = VideoProcessor()

@app.route('/')
def index():
    """Main page with video download form"""
    return render_template('index.html')

@app.route('/get_video_info', methods=['POST'])
def get_video_info():
    """Get video information without downloading"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        if not video_processor.is_valid_url(url):
            return jsonify({'error': 'Please enter a valid URL'}), 400
        
        if not video_processor.is_supported_platform(url):
            return jsonify({'error': 'This platform is not supported. Supported platforms: YouTube, Instagram, TikTok, Twitter/X'}), 400
        
        # Get video information
        video_info = video_processor.get_video_info(url)
        
        if video_info['error']:
            return jsonify({'error': video_info['error']}), 400
        
        return jsonify({
            'success': True,
            'title': video_info['title'],
            'duration': video_info['duration'],
            'thumbnail': video_info['thumbnail'],
            'uploader': video_info['uploader'],
            'formats': video_info['formats']
        })
        
    except Exception as e:
        logging.error(f"Error getting video info: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500

@app.route('/download_video', methods=['POST'])
def download_video():
    """Download video with selected format"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        format_id = data.get('format_id', 'best')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        if not video_processor.is_valid_url(url):
            return jsonify({'error': 'Please enter a valid URL'}), 400
        
        if not video_processor.is_supported_platform(url):
            return jsonify({'error': 'This platform is not supported'}), 400
        
        # Download video
        result = video_processor.download_video(url, format_id)
        
        if result['error']:
            return jsonify({'error': result['error']}), 400
        
        # Send file for download
        try:
            # Determine mimetype based on file extension
            file_ext = result['filename'].split('.')[-1].lower()
            if file_ext == 'mp3':
                mimetype = 'audio/mp3'
            elif file_ext == 'm4a':
                mimetype = 'audio/mp4'
            elif file_ext == 'mp4':
                mimetype = 'video/mp4'
            else:
                mimetype = 'application/octet-stream'
            
            return send_file(
                result['filepath'],
                as_attachment=True,
                download_name=result['filename'],
                mimetype=mimetype
            )
        except Exception as e:
            logging.error(f"Error sending file: {str(e)}")
            return jsonify({'error': 'Error sending file for download'}), 500
        
    except Exception as e:
        logging.error(f"Error downloading video: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred during download'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'video-downloader'})

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {str(error)}")
    return render_template('index.html'), 500
