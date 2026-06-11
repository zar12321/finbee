from fastapi import Request
from fastapi import HTTPException
from fastapi import status


def get_current_user(request: Request):

    user = request.session.get("user")

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login first"
        )

    return user


def get_current_user_id(request: Request):

    user = get_current_user(request)

    return user["user_id"]