"""
Auth controller
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from supabase import Client
from src.core.database import get_supabase
from src.core.session import create_session, delete_session, get_current_user_from_session, SESSION_COOKIE_NAME
from src.modules.auth.schema import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    response: Response,
    db: Client = Depends(get_supabase)
):
    """
    Login with email (no password required for now - development mode)
    
    Creates a session cookie that will be automatically sent with subsequent requests.
    No need to manually pass tokens - browser handles it automatically.
    """
    try:
        # Find user by email in users table
        user_response = db.table("users").select("*").eq("email", credentials.email).execute()
        
        if not user_response.data or len(user_response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"User with email {credentials.email} not found. Please sign up first."
            )
        
        user = user_response.data[0]
        
        # Create session cookie
        session_id = create_session(
            response=response,
            user_id=user["id"],
            email=user["email"]
        )
        
        return LoginResponse(
            access_token=session_id,  # Return session_id for reference
            user_id=user["id"],
            email=user["email"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/logout")
async def logout(
    response: Response,
    user_id: str = Depends(get_current_user_from_session)
):
    """
    Logout current user
    
    Deletes the session and clears the cookie.
    """
    # Get session_id from cookie to delete it
    from fastapi import Request
    
    # Clear cookie
    response.delete_cookie(key=SESSION_COOKIE_NAME)
    
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(
    user_id: str = Depends(get_current_user_from_session),
    db: Client = Depends(get_supabase)
):
    """
    Get current logged-in user info
    
    Use this to check if user is logged in and get their details.
    """
    # Get user from database
    response = db.table("users").select("*").eq("id", user_id).single().execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return response.data
