from fastapi import (
    APIRouter,
    Request,
    Form,
    Depends,
    status
)

from fastapi.responses import (
    RedirectResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from sqlalchemy.orm import Session

from app.database.connection import (
    get_db
)

from app.services.auth_service import (
    AuthService
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

templates = Jinja2Templates(
    directory="app/templates"
)


# =====================================================
# LOGIN PAGE
# =====================================================

@router.get("/login")
def login_page(
    request: Request
):
    success = request.query_params.get("success")
    reset = request.query_params.get("reset")

    success = True if success == "1" else False
    reset = True if reset == "1" else False

    return templates.TemplateResponse(
        request=request,
        name="auth/login.html",
        context={
            "request": request, 
            "success": success, 
            "reset": reset
        }
    )


# =====================================================
# LOGIN PROCESS
# =====================================================

@router.post("/login")
def login_process(
    request: Request,
    login_identifier: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):

    try:

        user = AuthService.login(
            db=db,
            login_identifier=login_identifier,
            password=password
        )

        request.session["user_id"] = (
            user.user_id
        )

        request.session["user_name"] = (
            user.nama
        )

        request.session["login_identifier"] = (
            user.login_identifier
        )

        request.session["login_type"] = (
            user.login_type
        )

        return RedirectResponse(
            url="/dashboard",
            status_code=status.HTTP_303_SEE_OTHER
        )

    except Exception as e:

        print("LOGIN ERROR:", e)

        return templates.TemplateResponse(
            request=request,
            name="auth/login.html",
            context={
                "request": request,
                "error": str(e)
            }
        )


# =====================================================
# REGISTER PAGE
# =====================================================

@router.get("/register")
def register_page(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="auth/register.html",
        context={
            "request": request
        }
    )


# =====================================================
# REGISTER PROCESS
# =====================================================

@router.post("/register")
def register_process(
    request: Request,
    nama: str = Form(...),
    login_identifier: str = Form(...),
    login_type: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    umur: int = Form(...),
    pekerjaan: str = Form(""),
    db: Session = Depends(get_db)
):

    try:

        AuthService.register(
            db=db,
            nama=nama,
            login_identifier=login_identifier,
            login_type=login_type,
            password=password,
            confirm_password=confirm_password,
            umur=umur,
            pekerjaan=pekerjaan
        )

        return RedirectResponse(
            url="/auth/login?success=1",
            status_code=status.HTTP_303_SEE_OTHER
        )

    except Exception as e:

        return templates.TemplateResponse(
            request=request,
            name="auth/register.html",
            context={
                "request": request
            }
        )


# =====================================================
# RESET PASSWORD PAGE
# =====================================================

@router.get("/reset-password")
def reset_password_page(
    request: Request
):


    return templates.TemplateResponse(
        request=request,
        name="auth/reset_password.html",
        context={
            "request": request
        }
    )


# =====================================================
# RESET PASSWORD PROCESS
# =====================================================

@router.post("/reset-password")
def reset_password_process(
    request: Request,
    login_identifier: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):

    try:

        AuthService.reset_password(
            db=db,
            login_identifier=login_identifier,
            new_password=new_password,
            confirm_password=confirm_password
        )

        return RedirectResponse(
            url="/auth/login?reset=1",
            status_code=status.HTTP_303_SEE_OTHER
        )

    except Exception as e:

        return templates.TemplateResponse(
            request=request,
            name="auth/reset_password.html",
            context={
                "request": request
            }
        )


# =====================================================
# LOGOUT
# =====================================================

@router.get("/logout")
def logout(
    request: Request
):

    request.session.clear()

    return RedirectResponse(
        url="/auth/login",
        status_code=status.HTTP_303_SEE_OTHER
    )