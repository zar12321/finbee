# app/routers/analysis.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.connection import (
    get_db
)

from app.dependencies.current_user import (
    get_current_user
)

from app.services.analysis_service import (
    AnalysisService
)

from app.database.db import (
    get_transactions_by_user_id
)

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    transactions_df = (
        get_transactions_by_user_id(
            db=db,
            user_id=current_user["user_id"]
        )
    )

    return AnalysisService.get_summary_metrics(
        transactions_df
    )


@router.get("/category")
def analyze_category(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    transactions_df = (
        get_transactions_by_user_id(
            db=db,
            user_id=current_user["user_id"]
        )
    )

    result = (
        AnalysisService.analyze_by_category(
            transactions_df
        )
    )

    return result.to_dict(
        orient="records"
    )


@router.get("/payment-method")
def analyze_payment_method(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    transactions_df = (
        get_transactions_by_user_id(
            db=db,
            user_id=current_user["user_id"]
        )
    )

    result = (
        AnalysisService.analyze_by_payment_method(
            transactions_df
        )
    )

    return result.to_dict(
        orient="records"
    )


@router.get("/monthly-trend")
def get_monthly_trend(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    transactions_df = (
        get_transactions_by_user_id(
            db=db,
            user_id=current_user["user_id"]
        )
    )

    result = (
        AnalysisService.get_monthly_trend(
            transactions_df
        )
    )

    return result.to_dict(
        orient="records"
    )


@router.get("/top-transactions")
def get_top_transactions(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    transactions_df = (
        get_transactions_by_user_id(
            db=db,
            user_id=current_user["user_id"]
        )
    )

    result = (
        AnalysisService.get_top_transactions(
            transactions_df,
            n=limit
        )
    )

    return result.to_dict(
        orient="records"
    )


@router.get("/prediction")
def get_prediction(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    try:

        return (
            AnalysisService.get_prediction(
                db=db,
                user_id=current_user["user_id"]
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )