# Overview

This is a web-based video downloader application built with Flask that allows users to download videos from multiple social media platforms including YouTube, Instagram, TikTok, and Twitter/X. The application provides a clean, responsive interface where users can paste video URLs, preview video information, and download content in various formats and qualities.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Vanilla JavaScript with Bootstrap 5 for responsive UI components
- **Theme**: Dark theme optimized for Replit environment using bootstrap-agent-dark-theme
- **Structure**: Template-based architecture using Jinja2 templates with a base template for consistent layout
- **Styling**: Custom CSS combined with Bootstrap classes for professional appearance
- **Icons**: Font Awesome for consistent iconography throughout the interface

## Backend Architecture
- **Framework**: Flask (Python) with modular route organization
- **Application Structure**: 
  - `app.py`: Core Flask application setup with proxy middleware
  - `main.py`: Application entry point for development server
  - `routes.py`: HTTP route handlers separated from core app logic
  - `video_processor.py`: Business logic for video processing operations
- **Session Management**: Flask sessions with configurable secret key
- **Error Handling**: Comprehensive exception handling with user-friendly error messages
- **Logging**: Built-in Python logging for debugging and monitoring

## Video Processing Engine
- **Core Library**: yt-dlp (YouTube-dl fork) for robust video extraction across platforms
- **Supported Platforms**: YouTube, Instagram, TikTok, Twitter/X with domain validation
- **Processing Features**:
  - URL validation and platform verification
  - Video metadata extraction (title, duration, thumbnail, uploader)
  - Format detection and quality options
  - Temporary file management for downloads

## Data Flow Architecture
- **Request Processing**: RESTful API endpoints returning JSON responses
- **Video Information Flow**: 
  1. URL validation and platform verification
  2. Metadata extraction without downloading
  3. Format and quality option presentation
  4. User-selected download execution
- **File Management**: Temporary directory usage for downloaded content with cleanup

## Security Considerations
- **Input Validation**: URL parsing and domain whitelist verification
- **Proxy Support**: ProxyFix middleware for deployment behind reverse proxies
- **Session Security**: Configurable session secret with environment variable support
- **Error Handling**: Sanitized error messages to prevent information disclosure

# External Dependencies

## Core Dependencies
- **Flask**: Web framework for HTTP handling and template rendering
- **yt-dlp**: Primary video extraction library supporting multiple platforms
- **Werkzeug**: WSGI utilities including ProxyFix middleware

## Frontend Dependencies
- **Bootstrap 5**: UI framework loaded via CDN for responsive design
- **Font Awesome 6**: Icon library for consistent visual elements
- **Replit Bootstrap Theme**: Dark theme CSS optimized for Replit environment

## Platform Integrations
- **YouTube**: Video extraction via yt-dlp's YouTube extractor
- **Instagram**: Social media content downloading through yt-dlp
- **TikTok**: Short-form video platform support
- **Twitter/X**: Social media video content extraction

## Infrastructure Dependencies
- **Python Standard Library**: 
  - `tempfile` for temporary file management
  - `urllib.parse` for URL parsing and validation
  - `logging` for application monitoring
  - `os` for environment variable access
- **Development Server**: Flask's built-in development server for local testing