"""
Chimera Agent: Social Media Operator
Publishes real content to Toutiao (头条号) and other Chinese social platforms.

Revenue: Platform creator fund earnings (头条号创作收益)
Real verification: Check Toutiao creator dashboard via Selenium/CDP

Current account: 西门有条河 (150 followers, ¥1.37 lifetime earnings)
Strategy: Increase posting frequency + quality → grow followers → more revenue

Available scripts:
- ~/toutiao_selenium.py — Selenium-based Toutiao publisher
- ~/china-social-tools/tools/social_publisher.py — Social publisher module
- ~/toutiao-news-archive/toutiao-content-prep.py — Content preparation
"""

import json
import pathlib
import datetime
import subprocess
import sys
import os
import urllib.request

ROOT = pathlib.Path(__file__).parent.parent
CHINA_SOCIAL_TOOLS = pathlib.Path.home() / "china-social-tools"
TOUTIAO_SELENIUM = pathlib.Path.home() / "toutiao_selenium.py"
TOUTIAO_CONTENT_PREP = pathlib.Path.home() / "toutiao-news-archive" / "toutiao-content-prep.py"

def execute(state):
    """
    Publish one micro-post to Toutiao using existing automation.
    """
    # Check if chrome is running with CDP
    cdp_running = check_cdp_available()
    
    if not cdp_running:
        return {
            "status": "skipped",
            "summary": "Chrome CDP not available — cannot publish to Toutiao. Start Chromium with --remote-debugging-port=9222",
        }
    
    # Try toutiao_selenium.py first (most reliable)
    if TOUTIAO_SELENIUM.exists():
        try:
            result = subprocess.run(
                [sys.executable, str(TOUTIAO_SELENIUM)],
                capture_output=True, text=True, timeout=120,
            )
            return {
                "status": "completed" if result.returncode == 0 else "failed",
                "summary": f"Toutiao publish via Selenium: {result.stdout[:200] if result.stdout else result.stderr[:200]}",
                "platform": "toutiao",
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "summary": "Toutiao Selenium publish timed out (120s)"}
        except Exception as e:
            return {"status": "error", "summary": f"Selenium error: {e}"}
    
    # Fallback: china-social-tools
    publisher = CHINA_SOCIAL_TOOLS / "tools" / "social_publisher.py"
    if publisher.exists():
        return {
            "status": "skipped",
            "summary": "social_publisher.py exists but needs import integration (not standalone script)",
        }
    
    return {
        "status": "skipped",
        "summary": "No Toutiao publishing script available. Need to start Chromium + run toutiao_selenium.py",
    }

def measure(state):
    """
    Measure real revenue from social media.
    Revenue requires dashboard access — track what we CAN verify for now.
    """
    post_count = len([h for h in state.get("history", [])
                      if "Toutiao publish" in h.get("execute_summary", "")])
    
    return {
        "revenue": 0.0,  # HONEST: Need dashboard scrape to verify real earnings
        "metrics": {
            "posts_total": post_count,
            "account": "西门有条河",
            "platform": "toutiao",
            "cdp_available": check_cdp_available(),
            "revenue_verification": "dashboard_scrape_needed",
        }
    }

def check_cdp_available():
    """Check if Chrome/Chromium CDP is available on port 9222"""
    try:
        req = urllib.request.urlopen("http://localhost:9222/json/version", timeout=3)
        return True
    except Exception:
        return False
