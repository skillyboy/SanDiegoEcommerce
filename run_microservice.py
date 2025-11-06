#!/usr/bin/env python
"""
Script to run the microservice alongside the Django application.
This script starts the FastAPI microservice on a different port.
"""

import os
import sys
import subprocess
import time
import signal
import argparse

# Default port for the microservice
DEFAULT_PORT = 8001

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run the microservice')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT,
                        help=f'Port to run the microservice on (default: {DEFAULT_PORT})')
    parser.add_argument('--reload', action='store_true',
                        help='Enable auto-reload for development')
    return parser.parse_args()

def run_microservice(port, reload=False):
    """Run the microservice using uvicorn"""
    reload_arg = "--reload" if reload else ""
    cmd = f"uvicorn microservice.main:app --host 0.0.0.0 --port {port} {reload_arg}"
    
    print(f"Starting microservice on port {port}...")
    print(f"Command: {cmd}")
    
    try:
        # Run the microservice
        process = subprocess.Popen(cmd, shell=True)
        
        # Handle graceful shutdown
        def signal_handler(sig, frame):
            print("\nShutting down microservice...")
            process.terminate()
            process.wait()
            sys.exit(0)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Wait for the process to complete
        process.wait()
    
    except KeyboardInterrupt:
        print("\nShutting down microservice...")
        process.terminate()
        process.wait()
    
    except Exception as e:
        print(f"Error running microservice: {e}")
        if process:
            process.terminate()
            process.wait()
        sys.exit(1)

if __name__ == "__main__":
    args = parse_args()
    run_microservice(args.port, args.reload)
