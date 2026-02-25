#!/usr/bin/env python3
"""
Railway API Deployment Script
Fully programmatic deployment without interactive CLI
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_railway_token():
    """Check if RAILWAY_TOKEN is set"""
    token = os.environ.get('RAILWAY_TOKEN')
    if not token:
        print("❌ RAILWAY_TOKEN environment variable not set\n")
        print("To get your Railway token:")
        print("1. Visit: https://railway.app/account/tokens")
        print("2. Click 'Create Token'")
        print("3. Copy the token")
        print("4. Run: export RAILWAY_TOKEN=your_token_here")
        print("\nThen run this script again.\n")
        sys.exit(1)
    return token

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} complete")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return None

def main():
    print_header("🚀 Railway Programmatic Deployment")
    
    # Step 1: Check token
    token = check_railway_token()
    print("✅ Railway token found")
    
    # Step 2: Check/Install Railway CLI
    print("\n⏳ Checking Railway CLI...")
    if subprocess.run("which railway", shell=True, capture_output=True).returncode != 0:
        print("⚠️  Railway CLI not found, installing...")
        run_command("npm install -g @railway/cli", "Railway CLI installation")
    else:
        print("✅ Railway CLI installed")
    
    # Step 3: Initialize or link project
    print("\n⏳ Checking Railway project...")
    
    # Check if railway.json exists
    if not Path("railway.json").exists():
        print("⚠️  No Railway project found, initializing...")
        project_name = "quant-backend"
        
        # Create project via CLI
        init_result = run_command(
            f'railway init --name {project_name}',
            "Railway project initialization"
        )
        
        if not init_result:
            print("❌ Failed to initialize Railway project")
            sys.exit(1)
    else:
        print("✅ Railway project found")
    
    # Step 4: Set environment variables
    print("\n⏳ Setting environment variables...")
    
    env_vars = {
        "PROJECT_NAME": "QuantBacktesting",
        "VERSION": "1.0.0",
        "API_V1_STR": "/api/v1",
        "ENVIRONMENT": "production",
        "DATABASE_URL": "sqlite+aiosqlite:///./quant.db",
        "PYTHONUNBUFFERED": "1",
        "PYTHONDONTWRITEBYTECODE": "1"
    }
    
    for key, value in env_vars.items():
        run_command(
            f'railway variables set {key}="{value}"',
            f"Setting {key}"
        )
    
    # Generate secure keys
    print("\n⏳ Generating secure keys...")
    secret_key = subprocess.run(
        "openssl rand -base64 64 | tr -d '\n'",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()
    
    jwt_secret = subprocess.run(
        "openssl rand -base64 64 | tr -d '\n'",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()
    
    run_command(f'railway variables set SECRET_KEY="{secret_key}"', "Setting SECRET_KEY")
    run_command(f'railway variables set JWT_SECRET_KEY="{jwt_secret}"', "Setting JWT_SECRET_KEY")
    
    print("✅ All environment variables set")
    
    # Step 5: Deploy
    print_header("🚀 Deploying to Railway")
    print("⚠️  This will take 3-5 minutes...\n")
    
    deploy_result = run_command(
        "railway up --detach",
        "Railway deployment"
    )
    
    if not deploy_result:
        print("❌ Deployment failed")
        sys.exit(1)
    
    # Step 6: Wait for deployment
    print("\n⏳ Waiting for deployment to complete...")
    for i in range(6):
        time.sleep(10)
        print(f"  Waiting... {(i+1)*10}s")
    
    # Step 7: Get deployment URL
    print("\n⏳ Fetching deployment URL...")
    url_result = run_command("railway domain", "Getting deployment URL")
    
    if url_result and "railway.app" in url_result:
        railway_url = url_result
    else:
        print("⚠️  Generating Railway domain...")
        run_command("railway domain", "Generating domain")
        time.sleep(5)
        railway_url = run_command("railway domain", "Getting deployment URL")
    
    # Step 8: Success!
    print_header("🎉 Deployment Complete!")
    
    if railway_url:
        print(f"🌐 Railway URL: https://{railway_url}\n")
        print("Test your deployment:")
        print(f"  curl https://{railway_url}/health")
        print(f"  curl https://{railway_url}/api/v1/backtesting/demo/strategies")
        print(f"\nAPI Docs: https://{railway_url}/api/v1/docs")
    else:
        print("⚠️  Deployment URL pending - check Railway dashboard")
    
    print("\nManagement commands:")
    print("  railway logs       - View logs")
    print("  railway status     - Check status")
    print("  railway open       - Open dashboard\n")
    
    # Save deployment info
    deployment_info = {
        "url": railway_url if railway_url else "pending",
        "deployed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "environment": "production"
    }
    
    with open("deployment_info.json", "w") as f:
        json.dump(deployment_info, f, indent=2)
    
    print("✅ Deployment info saved to deployment_info.json\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)
