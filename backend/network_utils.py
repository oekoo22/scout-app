"""
Network utilities for Scout App backend
"""

import socket
import subprocess
import platform
import re
from typing import List, Optional, Dict, Any

class NetworkUtils:
    """Utility class for network operations and IP detection"""
    
    @staticmethod
    def get_local_ip() -> Optional[str]:
        """
        Get the local network IP address using socket connection method
        This is the most reliable method across platforms
        """
        try:
            # Connect to a remote host to get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return None
    
    @staticmethod
    def get_all_local_ips() -> List[str]:
        """Get all local IP addresses on this machine"""
        ips = []
        
        try:
            hostname = socket.gethostname()
            # Get all IP addresses for this hostname
            for info in socket.getaddrinfo(hostname, None):
                ip = info[4][0]
                if ':' not in ip and ip != '127.0.0.1':  # IPv4 only, exclude localhost
                    ips.append(ip)
        except Exception:
            pass
        
        # Try alternative method using socket
        try:
            # Create a UDP socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            if ip not in ips:
                ips.append(ip)
        except Exception:
            pass
        
        return list(set(ips))  # Remove duplicates
    
    @staticmethod
    def get_network_interfaces() -> Dict[str, str]:
        """Get network interfaces and their IP addresses (Unix-like systems)"""
        interfaces = {}
        
        try:
            if platform.system() in ['Darwin', 'Linux']:
                # Use ifconfig command
                result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                if result.returncode == 0:
                    current_interface = None
                    for line in result.stdout.split('\n'):
                        # Check for interface name
                        if line and not line.startswith('\t') and not line.startswith(' '):
                            interface_match = re.match(r'^(\w+\d*)', line)
                            if interface_match:
                                current_interface = interface_match.group(1)
                        
                        # Check for inet address
                        elif current_interface and 'inet ' in line:
                            ip_match = re.search(r'inet (\d+\.\d+\.\d+\.\d+)', line)
                            if ip_match:
                                ip = ip_match.group(1)
                                if ip != '127.0.0.1':  # Exclude localhost
                                    interfaces[current_interface] = ip
            
        except Exception:
            pass
        
        return interfaces
    
    @staticmethod
    def is_port_available(host: str = 'localhost', port: int = 8000) -> bool:
        """Check if a port is available on the given host"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return False
    
    @staticmethod
    def find_available_port(host: str = 'localhost', start_port: int = 8000, max_attempts: int = 100) -> Optional[int]:
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            if NetworkUtils.is_port_available(host, port):
                return port
        return None
    
    @staticmethod
    def get_network_info() -> Dict[str, Any]:
        """Get comprehensive network information"""
        return {
            'primary_ip': NetworkUtils.get_local_ip(),
            'all_ips': NetworkUtils.get_all_local_ips(),
            'interfaces': NetworkUtils.get_network_interfaces(),
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'port_8000_available': NetworkUtils.is_port_available('0.0.0.0', 8000)
        }
    
    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate if a string is a valid IP address"""
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False
    
    @staticmethod
    def is_local_network_ip(ip: str) -> bool:
        """Check if an IP address is in a local network range"""
        if not NetworkUtils.validate_ip_address(ip):
            return False
        
        # Common private IP ranges
        private_ranges = [
            ('10.0.0.0', '10.255.255.255'),
            ('172.16.0.0', '172.31.255.255'),
            ('192.168.0.0', '192.168.255.255')
        ]
        
        ip_int = struct.unpack("!I", socket.inet_aton(ip))[0]
        
        for start, end in private_ranges:
            start_int = struct.unpack("!I", socket.inet_aton(start))[0]
            end_int = struct.unpack("!I", socket.inet_aton(end))[0]
            if start_int <= ip_int <= end_int:
                return True
        
        return False

# Import struct for IP range checking
import struct