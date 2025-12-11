"""
Authentication middleware for JWT tokens
"""
from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from supabase import Client
from src.core.database import get_supabase


async def get_current_user_id(
    authorization: Optional[str] = Header(None),
    db: Client = Depends(get_supabase)
) -> str:
    """
    Extract user_id from JWT token
    
    Uses Supabase's built-in auth.
    Token should be passed in Authorization header: Bearer <token>
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required"
        )
    
    try:
        # Extract token from "Bearer <token>"
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Use: Bearer <token>"
            )
        
        token = parts[1]
        
        # Verify token with Supabase auth
        user = db.auth.get_user(token)
        
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        return user.user.id
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )
