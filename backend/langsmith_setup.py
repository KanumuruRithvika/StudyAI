"""
LangSmith Configuration and Validation Module

Sets up complete LangSmith tracing for all agents in the workflow.
"""

import os
import sys
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

class LangSmithConfig:
    """Manages LangSmith configuration and validation"""
    
    def __init__(self):
        self.api_key = os.getenv("LANGCHAIN_API_KEY", "").strip()
        self.project_name = os.getenv("LANGCHAIN_PROJECT", "agentic-learning-system")
        self.tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "true").lower() == "true"
        self.langchain_endpoint = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com").strip()
    
    def validate(self) -> tuple[bool, str]:
        """
        Validate LangSmith configuration
        Returns: (is_valid, message)
        """
        errors = []
        
        # Check API key
        if not self.api_key:
            errors.append("[ERROR] LANGCHAIN_API_KEY not set in .env")
        elif len(self.api_key) < 20:
            errors.append("[ERROR] LANGCHAIN_API_KEY appears to be invalid (too short)")
        elif not self.api_key.startswith("lsv2_"):
            errors.append("[ERROR] LANGCHAIN_API_KEY should start with 'lsv2_'")
        
        # Check project name
        if not self.project_name:
            errors.append("[ERROR] LANGCHAIN_PROJECT not set in .env")
        
        # Check tracing enabled
        if not self.tracing_enabled:
            errors.append("[WARNING] LANGCHAIN_TRACING_V2 is not enabled (set to 'true')")
        
        if errors:
            return False, "\n".join(errors)
        
        return True, f"[OK] LangSmith configured:\n   Project: {self.project_name}\n   Tracing: Enabled\n   Endpoint: {self.langchain_endpoint}"
    
    def setup_environment(self):
        """Configure environment variables for LangSmith tracing"""
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = self.project_name
        os.environ["LANGCHAIN_API_KEY"] = self.api_key
        os.environ["LANGCHAIN_ENDPOINT"] = self.langchain_endpoint
    
    def get_dashboard_url(self) -> str:
        """Get the LangSmith dashboard URL for this project"""
        project_slug = self.project_name.lower().replace(" ", "-")
        return f"https://smith.langchain.com/o/projects/p/{project_slug}"
    
    def get_run_url(self, run_id: str) -> str:
        """Get the LangSmith run details URL"""
        project_slug = self.project_name.lower().replace(" ", "-")
        return f"https://smith.langchain.com/o/projects/p/{project_slug}/r/{run_id}"

def setup_langsmith():
    """
    Initialize and setup LangSmith for the entire application
    
    Returns:
        LangSmithConfig: Configured instance, or None if validation fails
    """
    config = LangSmithConfig()
    
    print("\n" + "="*70)
    print("[LANGSMITH SETUP]")
    print("="*70)
    
    # Validate configuration
    is_valid, message = config.validate()
    print(message)
    
    if not is_valid:
        print("\n[WARNING] LANGSMITH ISSUES DETECTED:")
        print("\nFix: Update your .env file with:")
        print("   LANGCHAIN_API_KEY=lsv2_pt_your_key_here")
        print("   LANGCHAIN_PROJECT=agentic-learning-system")
        print("   LANGCHAIN_TRACING_V2=true")
        print("\nGet API key from: https://smith.langchain.com/settings/organization/api-keys")
        print("="*70 + "\n")
        return None
    
    # Setup environment
    config.setup_environment()
    
    print(f"\nDashboard: {config.get_dashboard_url()}")
    print("="*70 + "\n")
    
    return config

def get_langsmith_config() -> Optional[LangSmithConfig]:
    """Get LangSmith configuration instance"""
    config = LangSmithConfig()
    if config.validate()[0]:
        config.setup_environment()
        return config
    return None
