from fastapi import (
    APIRouter,
    Request,
    Depends
)

from sqlalchemy.orm import Session

from fastapi.templating import (
    Jinja2Templates
)

from app.database.connection import (
    get_db
)

from app.dependencies.current_user import (
    get_current_user
)

from app.services import (
    dashboard_service
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

templates = Jinja2Templates(
    directory="app/templates"
)

# =====================================================
# DASHBOARD Page
# =====================================================
@router.get("")
def dashboard_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    metrics = dashboard_service.get_dashboard_metrics(
        db=db,
        user_id=current_user["user_id"]
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard/dashboard.html",
        context={
            "request": request,
            "user_name": current_user["nama"],
            "metrics": metrics
        }
    )


# =====================================================
# DASHBOARD Metrics
# =====================================================
@router.get("/metrics")
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return dashboard_service.get_dashboard_metrics(
        db=db,
        user_id=current_user["user_id"]
    )


# =====================================================
# TOP Categories
# =====================================================
@router.get("/top-categories")
def get_top_categories(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return dashboard_service.get_top_expense_categories(
        db=db,
        user_id=current_user["user_id"],
        limit=limit
    )


# =====================================================
# Monthly Summary
# =====================================================
@router.get("/monthly-summary")
def get_monthly_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return dashboard_service.get_monthly_summary(
        db=db,
        user_id=current_user["user_id"]
    )


# =====================================================
# Income
# =====================================================
@router.get("/income")
def get_total_income(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return {
        "total_income": dashboard_service.get_total_income(
            db=db,
            user_id=current_user["user_id"]
        )
    }


# =====================================================
# Expense
# =====================================================
@router.get("/expense")
def get_total_expense(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return {
        "total_expense": dashboard_service.get_total_expense(
            db=db,
            user_id=current_user["user_id"]
        )
    }


# =====================================================
# TOPUP
# =====================================================
@router.get("/topup")
def get_total_topup(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return {
        "total_topup": dashboard_service.get_total_topup(
            db=db,
            user_id=current_user["user_id"]
        )
    }


# =====================================================
# BALANCE
# =====================================================
@router.get("/balance")
def get_balance(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return {
        "balance": dashboard_service.get_current_balance(
            db=db,
            user_id=current_user["user_id"]
        )
    }