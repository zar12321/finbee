from fastapi import Request
from fastapi import HTTPException
from fastapi import status


def get_current_user(request: Request):

    user_id = request.session.get("user_id")

    if user_id is None:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login first"
        )

    return {
        "user_id": user_id,
        "nama": request.session.get("user_name"),
        "login_identifier": request.session.get("login_identifier"),
        "login_type": request.session.get("login_type")
    }

