#!/usr/bin/env python3
"""
Debug VNC connection issues
"""
import os
import socket
import subprocess
import sys

def check_port_availability(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def check_port_listening(port):
    """Check if something is listening on a port"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', port))
            return result == 0
    except:
        return False

def main():
    print("=== VNC Debug Information ===")
    
    # Check environment
    print(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
    print(f"QT_QPA_PLATFORM: {os.environ.get('QT_QPA_PLATFORM', 'Not set')}")
    print(f"QT_QPA_VNC_PORT: {os.environ.get('QT_QPA_VNC_PORT', 'Not set')}")
    
    # Check ports
    print("\n=== Port Status ===")
    for port in [5900, 5901, 5902]:
        available = check_port_availability(port)
        listening = check_port_listening(port)
        print(f"Port {port}: Available={available}, Listening={listening}")
    
    # Check processes
    print("\n=== Running Processes ===")
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        vnc_processes = [line for line in lines if 'vnc' in line.lower()]
        python_processes = [line for line in lines if 'python' in line and 'metapriv' in line]
        
        print("VNC processes:")
        for proc in vnc_processes:
            print(f"  {proc}")
            
        print("MetaprivBIDS processes:")
        for proc in python_processes:
            print(f"  {proc}")
    except Exception as e:
        print(f"Error checking processes: {e}")
    
    # Check network connections
    print("\n=== Network Connections ===")
    try:
        result = subprocess.run(['netstat', '-tlnp'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        port_5900_lines = [line for line in lines if '5900' in line]
        for line in port_5900_lines:
            print(f"  {line}")
    except Exception as e:
        print(f"Error checking network: {e}")

if __name__ == "__main__":
    main()
