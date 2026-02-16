from fastapi import APIRouter, Depends, status
from src.users.schemas import UserRegister, UserOut, TokenOut, UserLogin
from src.users.dependencies import get_user_service, get_current_user
from src.users.services import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    user_service: UserService = Depends(get_user_service)
) -> UserOut:

    """
    Register a new user.

    - **user_data**: UserRegister schema with first_name, last_name, username, email, password
    - Checks if email already exists
    - Hashes the password
    - Creates a new user in the database
    - Returns UserOut DTO
    - Raises 409 if email is already registered
    """
    
    return await user_service.register(user_data)

@router.post("/login", response_model=TokenOut, status_code=status.HTTP_200_OK)
async def Login(
    user_data: UserLogin,
    user_service: UserService = Depends(get_user_service)
) -> TokenOut:
    """
    Authenticate a user and return access and refresh tokens.

    - **user_data**: UserLogin schema with `email` and `password`
    - Validates credentials against database
    - Returns a JWT `access_token` and `refresh_token`
    - Raises 401 if credentials are invalid
    """
    return await user_service.login(user_data)

@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
async def read_current_user(
    current_user: UserOut = Depends(get_current_user)
) -> UserOut:
    """
    Get the currently authenticated user's information.

    - Requires a valid JWT access token in the Authorization header
    - Returns the user's details as a UserOut DTO
    - Raises 401 if the token is invalid or user not found
    """
    return current_user