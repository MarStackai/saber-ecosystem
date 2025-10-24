#!/usr/bin/env python3
"""
Saber Calculator Orchestrator
============================
A comprehensive orchestrator for managing the Saber Calculator ecosystem including:
- Streamlit web application
- AI agents
- Background services
- Health monitoring
"""

import os
import sys
import time
import signal
import subprocess
import threading
import logging
import json
from datetime import datetime
from pathlib import Path
import psutil
import requests
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('SaberOrchestrator')

class ServiceManager:
    """Manages individual services within the Saber ecosystem"""
    
    def __init__(self, name: str, command: List[str], port: Optional[int] = None, 
                 health_check_url: Optional[str] = None, working_dir: Optional[str] = None):
        self.name = name
        self.command = command
        self.port = port
        self.health_check_url = health_check_url
        self.working_dir = working_dir or os.getcwd()
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.start_time: Optional[datetime] = None
        
    def start(self) -> bool:
        """Start the service"""
        if self.is_running:
            logger.warning(f"Service {self.name} is already running")
            return True
            
        try:
            logger.info(f"Starting service: {self.name}")
            logger.info(f"Command: {' '.join(self.command)}")
            logger.info(f"Working directory: {self.working_dir}")
            
            self.process = subprocess.Popen(
                self.command,
                cwd=self.working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            self.is_running = True
            self.start_time = datetime.now()
            logger.info(f"Service {self.name} started with PID: {self.process.pid}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start service {self.name}: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the service"""
        if not self.is_running or not self.process:
            logger.warning(f"Service {self.name} is not running")
            return True
            
        try:
            logger.info(f"Stopping service: {self.name}")
            
            # Try graceful shutdown first
            self.process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning(f"Service {self.name} didn't stop gracefully, forcing...")
                self.process.kill()
                self.process.wait()
            
            self.is_running = False
            self.start_time = None
            logger.info(f"Service {self.name} stopped")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to stop service {self.name}: {e}")
            return False
    
    def restart(self) -> bool:
        """Restart the service"""
        logger.info(f"Restarting service: {self.name}")
        self.stop()
        time.sleep(2)  # Brief pause
        return self.start()
    
    def is_healthy(self) -> bool:
        """Check if the service is healthy"""
        if not self.is_running or not self.process:
            return False
            
        # Check if process is still alive
        if self.process.poll() is not None:
            self.is_running = False
            return False
        
        # If health check URL is provided, test it
        if self.health_check_url:
            try:
                response = requests.get(self.health_check_url, timeout=5)
                return response.status_code == 200
            except:
                return False
                
        # If port is specified, check if it's listening
        if self.port:
            try:
                for conn in psutil.net_connections():
                    if conn.laddr.port == self.port and conn.status == 'LISTEN':
                        return True
                return False
            except:
                pass
                
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get detailed status information"""
        status = {
            'name': self.name,
            'is_running': self.is_running,
            'is_healthy': self.is_healthy(),
            'pid': self.process.pid if self.process else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime': str(datetime.now() - self.start_time) if self.start_time else None,
            'port': self.port,
            'command': ' '.join(self.command)
        }
        
        # Add memory and CPU usage if process is running
        if self.process and self.is_running:
            try:
                proc = psutil.Process(self.process.pid)
                status['memory_mb'] = proc.memory_info().rss / 1024 / 1024
                status['cpu_percent'] = proc.cpu_percent()
            except:
                pass
                
        return status

class SaberOrchestrator:
    """Main orchestrator for the Saber Calculator ecosystem"""
    
    def __init__(self):
        self.services: Dict[str, ServiceManager] = {}
        self.is_running = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.setup_signal_handlers()
        
        # Define services
        self.define_services()
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
        sys.exit(0)
        
    def define_services(self):
        """Define all services that can be managed"""
        
        # Streamlit Calculator App
        self.services['streamlit'] = ServiceManager(
            name='Streamlit Calculator',
            command=['streamlit', 'run', 'calc-proto-cl.py', '--server.port=8501'],
            port=8501,
            health_check_url='http://localhost:8501',
            working_dir=os.getcwd()
        )
        
        # AI Agent Service (if you want to run it as a service)
        self.services['ai_agent'] = ServiceManager(
            name='AI Agent',
            command=['python3', 'my_first_agent.py'],
            working_dir=os.getcwd()
        )
        
        # Example background service (you can customize this)
        self.services['monitor'] = ServiceManager(
            name='System Monitor',
            command=['python3', '-c', '''
import time
import psutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemMonitor")

while True:
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    logger.info(f"System Status - CPU: {cpu}%, Memory: {memory}%")
    time.sleep(30)
'''],
            working_dir=os.getcwd()
        )
        
    def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
            
        return self.services[service_name].start()
        
    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
            
        return self.services[service_name].stop()
        
    def restart_service(self, service_name: str) -> bool:
        """Restart a specific service"""
        if service_name not in self.services:
            logger.error(f"Unknown service: {service_name}")
            return False
            
        return self.services[service_name].restart()
        
    def start_all(self, exclude: Optional[List[str]] = None) -> bool:
        """Start all services"""
        exclude = exclude or []
        logger.info("Starting all services...")
        
        success = True
        for name, service in self.services.items():
            if name not in exclude:
                if not service.start():
                    success = False
                    
        return success
        
    def stop_all(self) -> bool:
        """Stop all services"""
        logger.info("Stopping all services...")
        
        success = True
        for service in self.services.values():
            if not service.stop():
                success = False
                
        return success
        
    def get_status(self) -> Dict[str, Any]:
        """Get status of all services"""
        status = {
            'orchestrator': {
                'is_running': self.is_running,
                'start_time': datetime.now().isoformat(),
                'services_count': len(self.services)
            },
            'services': {}
        }
        
        for name, service in self.services.items():
            status['services'][name] = service.get_status()
            
        return status
        
    def print_status(self):
        """Print a formatted status report"""
        status = self.get_status()
        
        print("\n" + "="*60)
        print("SABER CALCULATOR ORCHESTRATOR STATUS")
        print("="*60)
        
        print(f"Orchestrator: {'RUNNING' if self.is_running else 'STOPPED'}")
        print(f"Services: {len(self.services)} total")
        print()
        
        for name, service_status in status['services'].items():
            health = "🟢" if service_status['is_healthy'] else "🔴"
            running = "RUNNING" if service_status['is_running'] else "STOPPED"
            
            print(f"{health} {name}: {running}")
            if service_status['pid']:
                print(f"    PID: {service_status['pid']}")
            if service_status['port']:
                print(f"    Port: {service_status['port']}")
            if service_status['uptime']:
                print(f"    Uptime: {service_status['uptime']}")
            if 'memory_mb' in service_status:
                print(f"    Memory: {service_status['memory_mb']:.1f} MB")
            print()
            
    def monitor_services(self):
        """Background monitoring of services"""
        logger.info("Starting service monitoring...")
        
        while self.is_running:
            try:
                for name, service in self.services.items():
                    if service.is_running and not service.is_healthy():
                        logger.warning(f"Service {name} appears unhealthy, attempting restart...")
                        service.restart()
                        
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)
                
    def start_monitoring(self):
        """Start the monitoring thread"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
            
        self.monitoring_thread = threading.Thread(target=self.monitor_services, daemon=True)
        self.monitoring_thread.start()
        
    def run(self, services: Optional[List[str]] = None, monitor: bool = True):
        """Run the orchestrator"""
        logger.info("Starting Saber Calculator Orchestrator...")
        self.is_running = True
        
        # Start specified services or all services
        if services:
            for service_name in services:
                self.start_service(service_name)
        else:
            # Default: start just the streamlit app
            self.start_service('streamlit')
            
        # Start monitoring if requested
        if monitor:
            self.start_monitoring()
            
        # Print initial status
        self.print_status()
        
        try:
            # Keep running until interrupted
            while self.is_running:
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal...")
            
        finally:
            self.shutdown()
            
    def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down orchestrator...")
        self.is_running = False
        
        # Stop all services
        self.stop_all()
        
        logger.info("Orchestrator shutdown complete")

def main():
    """Main entry point with CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Saber Calculator Orchestrator")
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'run'], 
                       help='Action to perform')
    parser.add_argument('--services', nargs='*', 
                       help='Specific services to operate on')
    parser.add_argument('--no-monitor', action='store_true',
                       help='Disable service monitoring')
    parser.add_argument('--daemon', action='store_true',
                       help='Run in daemon mode')
    
    args = parser.parse_args()
    
    orchestrator = SaberOrchestrator()
    
    if args.action == 'run':
        orchestrator.run(services=args.services, monitor=not args.no_monitor)
        
    elif args.action == 'start':
        if args.services:
            for service in args.services:
                orchestrator.start_service(service)
        else:
            orchestrator.start_all()
        orchestrator.print_status()
        
    elif args.action == 'stop':
        if args.services:
            for service in args.services:
                orchestrator.stop_service(service)
        else:
            orchestrator.stop_all()
            
    elif args.action == 'restart':
        if args.services:
            for service in args.services:
                orchestrator.restart_service(service)
        else:
            orchestrator.stop_all()
            time.sleep(2)
            orchestrator.start_all()
        orchestrator.print_status()
        
    elif args.action == 'status':
        orchestrator.print_status()

if __name__ == '__main__':
    main()
