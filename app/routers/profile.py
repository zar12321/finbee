# app/routers/profile.py

from fastapi import (
    APIRouter,
    Depends,
    Query
)

from sqlalchemy.orm import Session

from app.database.connection import (
    get_db
)

from app.dependencies.current_user import (
    get_current_user
)

from app.services.profile_service import (
    ProfileService
)

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)


# =====================================================
# GET PROFILE
# =====================================================

@router.get("/")
def get_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return ProfileService.get_profile(
        db=db,
        user_id=current_user["user_id"]
    )


# =====================================================
# FINANCIAL SUMMARY
# =====================================================

@router.get("/financial-summary")
def get_financial_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return ProfileService.get_financial_summary(
        db=db,
        user_id=current_user["user_id"]
    )


# =====================================================
# GET MONTHLY PLAN
# =====================================================

@router.get("/monthly-plan")
def get_monthly_plan(
    bulan: int | None = Query(None),
    tahun: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    return ProfileService.get_monthly_plan(
        db=db,
        user_id=current_user["user_id"],
        bulan=bulan,
        tahun=tahun
    )


# =====================================================
# SAVE MONTHLY TARGET
# =====================================================

@router.post("/monthly-plan")
def save_monthly_target(
    pemasukan_bulanan: float,
    target_bulanan: float,
    bulan: int | None = Query(None),
    tahun: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    ProfileService.save_monthly_target(
        db=db,
        user_id=current_user["user_id"],
        pemasukan_bulanan=pemasukan_bulanan,
        target_bulanan=target_bulanan,
        bulan=bulan,
        tahun=tahun
    )

    return {
        "success": True,
        "message": (
            "Target bulanan berhasil disimpan."
        )
    }