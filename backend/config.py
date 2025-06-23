import os
import logging
from typing import Optional
from network_utils import NetworkUtils

class Config:
    """Configuration class for Scout App backend"""
    
    def __init__(self):
        # Environment detection
        self.environment = os.getenv('SCOUT_ENV', 'development')
        
        # Server configuration
        self.host = os.getenv('SCOUT_HOST', '0.0.0.0')
        self.port = int(os.getenv('SCOUT_PORT', '8000'))
        
        # Network configuration
        self.local_ip = NetworkUtils.get_local_ip()
        self.all_local_ips = NetworkUtils.get_all_local_ips()
        self.use_local_ip = os.getenv('SCOUT_USE_LOCAL_IP', 'false').lower() == 'true'
        
        # OAuth configuration - initialize after network config
        self.oauth_redirect_uri = self._get_oauth_redirect_uri()
        self.oauth_base_host = self._get_oauth_base_host()
        
        # CORS configuration
        self.cors_origins = self._get_cors_origins()
        
        # Debug mode
        self.debug = os.getenv('SCOUT_DEBUG', 'true').lower() == 'true'
        
        # Setup logging
        self._setup_logging()
        
        # Validate configuration on startup
        self._validate_oauth_config()
        
    def get_network_info(self) -> dict:
        """Get comprehensive network information"""
        return NetworkUtils.get_network_info()
    
    def _get_oauth_redirect_uri(self) -> str:
        """Get the appropriate OAuth redirect URI based on configuration"""
        # Check for explicit override first
        explicit_redirect = os.getenv('SCOUT_OAUTH_REDIRECT_URI')
        if explicit_redirect:
            return explicit_redirect
        
        # Determine the appropriate host for OAuth redirect
        oauth_host = self._get_oauth_base_host()
        return f"http://{oauth_host}:{self.port}/auth/google/callback"
    
    def _get_oauth_base_host(self) -> str:
        """Get the base host for OAuth redirects"""
        # Check for explicit OAuth host override
        oauth_host = os.getenv('SCOUT_OAUTH_HOST')
        if oauth_host:
            return oauth_host
            
        # For development, use localhost by default for Google OAuth compatibility  
        # Google OAuth requires the redirect URI to match exactly what's configured
        # in Google Console, and localhost is typically what's configured there
        if self.environment == 'development':
            return 'localhost'
        
        # For production or when explicitly using local IP
        if self.use_local_ip and self.local_ip:
            return self.local_ip
        
        return 'localhost'
    
    def _get_base_url(self) -> str:
        """Get the base URL for the application"""
        if self.use_local_ip and self.local_ip:
            return f"http://{self.local_ip}:{self.port}"
        else:
            return f"http://localhost:{self.port}"
    
    def _get_cors_origins(self) -> list:
        """Get CORS origins based on configuration"""
        origins = []
        
        # Always allow localhost for development
        origins.extend([
            f"http://localhost:{self.port}",
            "http://localhost:3000",  # Common frontend dev server
            "http://127.0.0.1:{self.port}",
        ])
        
        # Add local IP if available
        if self.local_ip:
            origins.extend([
                f"http://{self.local_ip}:{self.port}",
                f"https://{self.local_ip}:{self.port}",
            ])
        
        # Add custom origins from environment
        custom_origins = os.getenv('SCOUT_CORS_ORIGINS', '').split(',')
        origins.extend([origin.strip() for origin in custom_origins if origin.strip()])
        
        return origins
    
    def _setup_logging(self):
        """Setup logging configuration"""
        level = logging.INFO if self.debug else logging.WARNING
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(f"{__name__}.Config")
    
    def _validate_oauth_config(self):
        """Validate OAuth configuration and warn about potential issues"""
        if not hasattr(self, 'logger'):
            return  # Skip if logging not set up yet
            
        # Check if OAuth redirect URI is accessible
        oauth_host = self.oauth_base_host
        if oauth_host == 'localhost' and self.use_local_ip:
            self.logger.warning(
                f"⚠️  OAuth redirect URI uses 'localhost' but server runs on local IP ({self.local_ip}). "
                f"Mobile devices won't be able to complete OAuth flow. "
                f"Consider setting SCOUT_OAUTH_HOST={self.local_ip} or ensure Google Console is configured for localhost."
            )
        
        # Check if we have a valid local IP when using local IP mode
        if self.use_local_ip and not self.local_ip:
            self.logger.error(
                "❌ SCOUT_USE_LOCAL_IP is enabled but no local IP could be detected. "
                "OAuth redirects may fail."
            )
        
        self.logger.info(f"🔗 OAuth redirect URI: {self.oauth_redirect_uri}")
        self.logger.info(f"🌐 Server accessible at: {self._get_base_url()}")
    
    def get_info(self) -> dict:
        """Get configuration information for debugging"""
        return {
            'environment': self.environment,
            'host': self.host,
            'port': self.port,
            'local_ip': self.local_ip,
            'all_local_ips': self.all_local_ips,
            'use_local_ip': self.use_local_ip,
            'base_url': self._get_base_url(),
            'oauth_redirect_uri': self.oauth_redirect_uri,
            'oauth_base_host': self.oauth_base_host,
            'cors_origins': self.cors_origins,
            'debug': self.debug,
            'network_info': self.get_network_info(),
            'oauth_config_warnings': self._get_oauth_warnings()
        }
    
    def _get_oauth_warnings(self) -> list:
        """Get list of OAuth configuration warnings"""
        warnings = []
        
        if self.oauth_base_host == 'localhost' and self.use_local_ip:
            warnings.append(
                "OAuth uses localhost but server runs on local IP - mobile devices may not be able to complete OAuth"
            )
        
        if self.use_local_ip and not self.local_ip:
            warnings.append(
                "Local IP mode enabled but no local IP detected"
            )
        
        return warnings

# Global configuration instance
config = Config()