#!/usr/bin/env python3
"""
Configuration Migration Script

This script helps migrate from the old scattered configuration system
to the new centralized configuration management system.
"""

import os
import json
import tomllib
import shutil
from pathlib import Path
from typing import Dict, Any

def backup_existing_configs():
    """Backup existing configuration files."""
    backup_dir = Path("config_backup")
    backup_dir.mkdir(exist_ok=True)
    
    print("📦 Backing up existing configuration files...")
    
    # Files to backup
    config_files = [
        "OpenManus/config/config.toml",
        "enhanced_agent/config/mcp.json",
        "enhanced_agent/config/mcp_extended.json",
        ".env",
        "config.toml",
    ]
    
    backed_up = []
    for config_file in config_files:
        if Path(config_file).exists():
            backup_path = backup_dir / Path(config_file).name
            shutil.copy2(config_file, backup_path)
            backed_up.append(config_file)
            print(f"  ✅ {config_file} → {backup_path}")
    
    if backed_up:
        print(f"✅ Backed up {len(backed_up)} configuration files to {backup_dir}")
    else:
        print("ℹ️  No existing configuration files found to backup")
    
    return backed_up


def migrate_openmanus_config():
    """Migrate OpenManus configuration to new system."""
    config_file = Path("OpenManus/config/config.toml")
    if not config_file.exists():
        print("ℹ️  No OpenManus config.toml found")
        return {}
    
    print("🔄 Migrating OpenManus configuration...")
    
    with open(config_file, 'rb') as f:
        old_config = tomllib.load(f)
    
    # Extract LLM configuration
    llm_config = {}
    if 'llm' in old_config:
        llm_data = old_config['llm']
        llm_config = {
            'provider': 'openai',  # Default
            'model': llm_data.get('model', 'gpt-3.5-turbo'),
            'api_key': llm_data.get('api_key'),
            'base_url': llm_data.get('base_url'),
            'max_tokens': llm_data.get('max_tokens', 2048),
            'temperature': llm_data.get('temperature', 0.1),
        }
        
        # Detect provider type
        if 'api_type' in llm_data:
            if llm_data['api_type'] == 'azure':
                llm_config['provider'] = 'azure'
                llm_config['api_version'] = llm_data.get('api_version')
            elif llm_data['api_type'] == 'ollama':
                llm_config['provider'] = 'ollama'
        elif 'anthropic' in str(llm_data.get('base_url', '')).lower():
            llm_config['provider'] = 'anthropic'
    
    # Extract browser configuration (for future use)
    browser_config = old_config.get('browser', {})
    
    print("  ✅ OpenManus configuration migrated")
    return {
        'llm': llm_config,
        'browser': browser_config
    }


def migrate_mcp_config():
    """Migrate MCP configuration to new system."""
    config_files = [
        "enhanced_agent/config/mcp_extended.json",
        "enhanced_agent/config/mcp.json"
    ]
    
    mcp_config = {'servers': {}, 'default_server': 'llama-mcp'}
    
    for config_file in config_files:
        if Path(config_file).exists():
            print(f"🔄 Migrating {config_file}...")
            
            with open(config_file, 'r') as f:
                old_config = json.load(f)
            
            # Merge servers
            if 'servers' in old_config:
                mcp_config['servers'].update(old_config['servers'])
            
            # Update default server
            if 'default_server' in old_config:
                mcp_config['default_server'] = old_config['default_server']
            
            print(f"  ✅ {config_file} migrated")
    
    if mcp_config['servers']:
        print(f"✅ Migrated {len(mcp_config['servers'])} MCP servers")
    
    return mcp_config


def migrate_env_file():
    """Migrate .env file variables."""
    env_file = Path(".env")
    if not env_file.exists():
        print("ℹ️  No .env file found")
        return {}
    
    print("🔄 Migrating .env file...")
    
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"\'')
    
    print(f"  ✅ Found {len(env_vars)} environment variables")
    return env_vars


def create_new_config_files(openmanus_config, mcp_config, env_vars):
    """Create new centralized configuration files."""
    print("📝 Creating new configuration files...")
    
    # Ensure config directory exists
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    # Update environment-specific configs with migrated data
    environments = ['development', 'staging', 'production']
    
    for env in environments:
        config_file = config_dir / f"config.{env}.toml"
        if config_file.exists():
            print(f"  ⚠️  {config_file} already exists, skipping...")
            continue
        
        # Read template and update with migrated data
        template_file = config_dir / f"config.{env}.toml"
        if template_file.exists():
            with open(template_file, 'rb') as f:
                config_data = tomllib.load(f)
            
            # Update LLM section with migrated data
            if 'llm' in openmanus_config and openmanus_config['llm']:
                llm_data = openmanus_config['llm']
                if 'llm' in config_data:
                    config_data['llm'].update({
                        k: v for k, v in llm_data.items() 
                        if v is not None and k != 'api_key'  # Don't override API key
                    })
        
        print(f"  ✅ Updated {config_file}")
    
    # Write consolidated MCP configuration
    mcp_file = config_dir / "mcp.json"
    if not mcp_file.exists() and mcp_config['servers']:
        with open(mcp_file, 'w') as f:
            json.dump(mcp_config, f, indent=2)
        print(f"  ✅ Created {mcp_file}")
    
    # Update .env file with any missing variables
    env_file = Path(".env")
    required_vars = ['OPENAI_API_KEY', 'ENVIRONMENT']
    missing_vars = []
    
    for var in required_vars:
        if var not in env_vars:
            missing_vars.append(var)
    
    if missing_vars:
        with open(env_file, 'a') as f:
            f.write("\n# Added by migration script\n")
            for var in missing_vars:
                if var == 'ENVIRONMENT':
                    f.write(f"{var}=development\n")
                else:
                    f.write(f"# {var}=your_key_here\n")
        print(f"  ✅ Added {len(missing_vars)} variables to .env")


def install_dependencies():
    """Install required dependencies for the new configuration system."""
    print("📦 Installing configuration management dependencies...")
    
    try:
        import subprocess
        
        # Install using the virtual environment
        cmd = ["./virtual/bin/pip", "install", "-r", "config/requirements.txt"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✅ Dependencies installed successfully")
        else:
            print(f"  ❌ Error installing dependencies: {result.stderr}")
            print("  💡 Try running manually: ./virtual/bin/pip install -r config/requirements.txt")
    
    except Exception as e:
        print(f"  ❌ Error installing dependencies: {e}")
        print("  💡 Try running manually: ./virtual/bin/pip install -r config/requirements.txt")


def test_new_config():
    """Test the new configuration system."""
    print("🧪 Testing new configuration system...")
    
    try:
        # Test basic import and functionality
        from config.settings import get_config, get_llm_config, get_mcp_server_config
        
        config = get_config()
        print(f"  ✅ Main config loaded: {config.environment} environment")
        
        llm_config = get_llm_config()
        print(f"  ✅ LLM config loaded: {llm_config.provider} provider")
        
        mcp_servers = list(config.mcp_servers.keys())
        print(f"  ✅ MCP config loaded: {len(mcp_servers)} servers")
        
        print("✅ New configuration system is working!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error testing configuration: {e}")
        print("  💡 Check that all dependencies are installed")
        return False


def main():
    """Main migration function."""
    print("🚀 OMD Configuration Migration Tool")
    print("=" * 50)
    print("This will migrate your existing configuration to the new centralized system.")
    print()
    
    # Backup existing configs
    backed_up = backup_existing_configs()
    print()
    
    # Migrate configurations
    openmanus_config = migrate_openmanus_config()
    mcp_config = migrate_mcp_config()
    env_vars = migrate_env_file()
    print()
    
    # Create new configuration files
    create_new_config_files(openmanus_config, mcp_config, env_vars)
    print()
    
    # Install dependencies
    install_dependencies()
    print()
    
    # Test new configuration
    if test_new_config():
        print()
        print("🎉 Migration completed successfully!")
        print()
        print("Next steps:")
        print("1. Review the new configuration files in the config/ directory")
        print("2. Update your API keys in the .env file")
        print("3. Test the application: ./run_streamlit.sh")
        print("4. Check the configuration example: python config/example.py")
        print()
        print("Your old configuration files are backed up in config_backup/")
    else:
        print()
        print("❌ Migration completed with errors")
        print("Please check the error messages and try manual configuration")


if __name__ == "__main__":
    main()

