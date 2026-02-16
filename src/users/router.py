from fastapi import APIRouter, Depends, status
from src.users.schemas import UserRegister, UserOut
from src.users.dependencies import get_user_service
from src.users.services import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    user_service: UserService = Depends(get_user_service)) -> UserOut:

    """
    Register a new user.
    
    - Checks if email already exists
    - Hashes the password
    - Creates a new user in the database
    - Returns UserOut DTO
    """
    
    return await user_service.register(user_data)

