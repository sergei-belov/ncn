from typing import Annotated

from fastapi import APIRouter, Depends, Form, status

from api.dependencies.http import get_user
from api.managers import Managers
from models import pydantic


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.get("/me", response_model=pydantic.UserAPI)
async def get_me(
    user: Annotated[pydantic.UserDTO, Depends(get_user)],
) -> pydantic.UserAPI:
    """Return the authenticated user's public profile."""

    return pydantic.UserAPI.model_validate(user)


@router.post(
    "/register",
    response_model=pydantic.PostRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_info: pydantic.PostRegisterRequest,
) -> pydantic.PostRegisterResponse:
    """Register a user through the configured local authentication flow."""

    return await Managers.auth.register(user_info)


@router.post("/jwt/login", response_model=pydantic.PostLoginResponse)
async def login(
    username: Annotated[str, Form(min_length=3, max_length=100)],
    password: Annotated[str, Form(min_length=8, max_length=128)],
) -> pydantic.PostLoginResponse:
    """Authenticate local credentials and return a bearer token."""

    return await Managers.auth.login(username, password)
