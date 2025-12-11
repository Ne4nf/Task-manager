"""
Simple session management
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import Cookie, Response, HTTPException, status, Header

# In-memory session store
# Key: session_id, Value: {"user_id": str, "email": str, "expires": datetime}
_sessions: Dict[str, dict] = {}

SESSION_COOKIE_NAME = "session_id"
SESSION_DURATION = timedelta(hours=24)  # 24 hours


def create_session(response: Response, user_id: str, email: str) -> str:
    """
    Create a new session and set cookie
    
    Returns session_id
    """
    import secrets
    
    session_id = secrets.token_urlsafe(32)
    
    _sessions[session_id] = {
        "user_id": user_id,
        "email": email,
        "expires": datetime.utcnow() + SESSION_DURATION
    }
    
    # Set cookie with SameSite=None for cross-origin (development)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=session_id,
        httponly=True,
        max_age=int(SESSION_DURATION.total_seconds()),
        samesite="none",  # Changed from "lax" to "none" for cross-origin
        secure=False  # Set True in production with HTTPS
    )
    
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    """
    Get session data by session_id
    
    Returns None if session not found or expired
    """
    if session_id not in _sessions:
        return None
    
    session = _sessions[session_id]
    
    # Check if expired
    if datetime.utcnow() > session["expires"]:
        # Clean up expired session
        del _sessions[session_id]
        return None
    
    return session


def delete_session(session_id: str):
    """Delete a session"""
    if session_id in _sessions:
        del _sessions[session_id]


def get_current_user_from_session(
    session_id: Optional[str] = Cookie(None, alias=SESSION_COOKIE_NAME),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID")
) -> str:
    """
    Dependency to get current user_id from session cookie OR X-User-ID header
    
    Supports both:
    1. Session cookie (preferred)
    2. X-User-ID header (for compatibility with current frontend)
    
    Raises 401 if no valid session/user found
    """
    # Try X-User-ID header first (current frontend implementation)
    if x_user_id:
        return x_user_id
    
    # Fall back to session cookie
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please login first."
        )
    
    session = get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please login again."
        )
    
    return session["user_id"]
