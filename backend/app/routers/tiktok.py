from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel

from app.database import get_db
from app.services.auth import get_current_active_user
from app.services.tiktok_api import get_tiktok_manager, TikTokAPIClient
from app import models

router = APIRouter()

class ToggleRequest(BaseModel):
    running: bool

class PublishRequest(BaseModel):
    video_url: str
    title: str
    privacy_level: str = "PUBLIC_TO_EVERYONE"

@router.get("/status")
def get_status(current_user: models.User = Depends(get_current_active_user)):
    """Get the current TikTok automation dashboard status"""
    manager = get_tiktok_manager()
    return manager.state

@router.post("/toggle")
def toggle_automation(req: ToggleRequest, current_user: models.User = Depends(get_current_active_user)):
    """Activate or deactivate set-and-forget autopilot mode"""
    manager = get_tiktok_manager()
    return manager.toggle_automation(req.running)

@router.post("/simulate-tick")
def force_tick(current_user: models.User = Depends(get_current_active_user)):
    """Manually trigger a simulation cycle cycle (for testing/sandbox demo)"""
    manager = get_tiktok_manager()
    if not manager.state["is_running"]:
        raise HTTPException(status_code=400, detail="Automation is not running. Please start it first.")
    manager.simulate_cycle()
    return manager.state

@router.post("/reset")
def reset_status(current_user: models.User = Depends(get_current_active_user)):
    """Reset simulation stats and logs back to default state"""
    manager = get_tiktok_manager()
    manager.set_default_state()
    return manager.state

@router.get("/auth-url")
def get_auth_url(current_user: models.User = Depends(get_current_active_user)):
    """Retrieve TikTok Content Posting API authorization URL"""
    client = TikTokAPIClient()
    if not client.is_configured():
        return {
            "configured": False,
            "url": None,
            "message": "TikTok API key parameters are not set in the server environment (.env). Operating in sandbox mode."
        }
    return {
        "configured": True,
        "url": client.get_authorization_url(state=f"user_{current_user.id}")
    }

@router.post("/publish")
def publish_video(req: PublishRequest, current_user: models.User = Depends(get_current_active_user)):
    """Publish a video using the TikTok API or simulate it in sandbox mode"""
    client = TikTokAPIClient()
    manager = get_tiktok_manager()
    
    if not client.is_configured():
        # Sandbox publication
        manager.state["content_generated"] += 1
        manager.state["auto_posted"] += 1
        manager.add_log("success", f"Sandbox Publish: Video '{req.title}' successfully published to simulated TikTok API.")
        manager.save_state()
        return {
            "success": True,
            "sandbox": True,
            "message": "Video published successfully in sandbox mode."
        }
    else:
        # Real publishing requires user to complete OAuth flow first
        # In a real environment, we check user's saved credentials in database
        # For this setup, we simulate it if the user doesn't have an active oauth token
        return {
            "success": False,
            "message": "TikTok account oauth token missing. Please complete login flow first."
        }
