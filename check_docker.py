#!/usr/bin/env python3
"""
Docker Deployment Assistant
Checks Docker installation and guides through deployment
"""

import subprocess
import sys
import os
import platform

def check_command(cmd):
    """Check if a command is available"""
    try:
        result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
        return result.returncode == 0, result.stdout.strip()
    except Exception as e:
        return False, str(e)

def main():
    print("\n" + "="*70)
    print("🐳 DOCKER DEPLOYMENT CHECKER")
    print("="*70 + "\n")
    
    # Check Docker
    print("[1] Checking Docker Installation...")
    docker_ok, docker_version = check_command('docker')
    if docker_ok:
        print(f"    ✓ {docker_version}")
    else:
        print(f"    ✗ Docker not installed")
        print(f"\n    Install from: https://www.docker.com/products/docker-desktop")
        print(f"    Platform: {platform.system()}")
        return False
    
    # Check Docker Compose
    print("\n[2] Checking Docker Compose Installation...")
    compose_ok, compose_version = check_command('docker-compose')
    if compose_ok:
        print(f"    ✓ {compose_version}")
    else:
        print(f"    ✗ Docker Compose not installed")
        print(f"\n    Install from: https://docs.docker.com/compose/install/")
        return False
    
    # Check if Docker daemon is running
    print("\n[3] Checking Docker Daemon...")
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("    ✓ Docker daemon is running")
        else:
            print("    ✗ Docker daemon is not running")
            print("    Start Docker Desktop or run: sudo systemctl start docker")
            return False
    except Exception as e:
        print(f"    ✗ Error: {e}")
        return False
    
    print("\n" + "="*70)
    print("✅ ALL CHECKS PASSED - Ready to deploy!")
    print("="*70 + "\n")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
