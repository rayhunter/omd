#!/usr/bin/env python3
"""
Setup script to create .env file with proper environment variables.
"""

import os
from pathlib import Path

def create_env_file():
    """Create a .env file with template values."""
    
    env_content = """# OpenAI API Key for DSPy integration (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Optional: News API (for news-api server)
# Get your free API key from: https://newsapi.org/
# NEWS_API_KEY=your_news_api_key_here

# Optional: OpenWeatherMap API (for weather server)  
# Get your free API key from: https://openweathermap.org/api
# WEATHER_API_KEY=your_weather_api_key_here

# Optional: GitHub Token (for github server - increases rate limits)
# Generate a personal access token from: https://github.com/settings/tokens
# GITHUB_TOKEN=your_github_token_here
"""
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("📁 .env file already exists!")
        
        # Check if it has OPENAI_API_KEY
        with open(env_file, 'r') as f:
            content = f.read()
            
        if "OPENAI_API_KEY=" in content and "your_openai_api_key_here" not in content:
            print("✅ .env file appears to have a real OpenAI API key set")
            return True
        else:
            print("⚠️  .env file exists but may need OpenAI API key")
            print("🔍 Please check that OPENAI_API_KEY is set to your actual API key")
            return False
    else:
        print("📝 Creating .env file template...")
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created!")
        print()
        print("🔑 IMPORTANT: Edit the .env file and replace 'your_openai_api_key_here' with your actual OpenAI API key")
        print("💡 Get your API key from: https://platform.openai.com/api-keys")
        return False

def main():
    print("🚀 Setting up environment variables for OMD project")
    print("=" * 50)
    
    if create_env_file():
        print("\n✅ Environment setup complete!")
    else:
        print("\n⚠️  Please edit .env file with your actual API keys before running the application")
        print()
        print("📝 After editing .env, restart the Streamlit application:")
        print("   ./run_streamlit.sh")

if __name__ == "__main__":
    main()
