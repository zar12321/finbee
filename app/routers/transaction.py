# app/routers/transaction.py

from io import BytesIO

import pandas as pd

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException
)

from sqlalchemy.orm import Session

from app.database.connection import (
    get_db
)

from app.dependencies.current_user import (
    get_current_user
)

from app.services.transaction_service import (
    TransactionService
)

from app.schemas.transaction import (
    TransactionCreateRequest,
    TransactionUpdateRequest,
    TransactionResponse,
    TransactionActionResponse
)

from core.import_file import (
    auto_clean_financial_file
)

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)


# =====================================================
# GET ALL TRANSACTIONS
# =====================================================

@router.get(
    "/",
    response_model=list[TransactionResponse]
)
def get_transactions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    transactions = (
        TransactionService.get_transactions(
            db=db,
            user_id=current_user["user_id"]
        )
    )

    return transactions.to_dict(
        orient="records"
    )


# =====================================================
# GET CATEGORIES
# =====================================================

@router.get("/categories")
def get_categories(
    db: Session = Depends(get_db)
):

    categories = (
        TransactionService.get_categories(
            db=db
        )
    )

    return categories.to_dict(
        orient="records"
    )


# =====================================================
# CREATE TRANSACTION
# =====================================================

@router.post(
    "/",
    response_model=TransactionActionResponse
)
def create_transaction(
    request: TransactionCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    TransactionService.create_transaction(
        db=db,
        user_id=current_user["user_id"],
        category_id=request.category_id,
        tanggal_transaksi=request.tanggal_transaksi,
        transaction_type=request.transaction_type,
        tujuan_transaksi=request.tujuan_transaksi,
        keterangan=request.keterangan,
        payment_method=request.payment_method,
        amount=request.amount,
        raw_category=request.raw_category
    )

    return TransactionActionResponse(
        success=True,
        message="Transaksi berhasil dibuat."
    )


# =====================================================
# UPDATE TRANSACTION
# =====================================================

@router.put(
    "/{transaction_id}",
    response_model=TransactionActionResponse
)
def update_transaction_data(
    transaction_id: int,
    request: TransactionUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    TransactionService.edit_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user["user_id"],
        category_id=request.category_id,
        tanggal_transaksi=request.tanggal_transaksi,
        transaction_type=request.transaction_type,
        tujuan_transaksi=request.tujuan_transaksi,
        keterangan=request.keterangan,
        payment_method=request.payment_method,
        amount=request.amount,
        raw_category=request.raw_category
    )

    return TransactionActionResponse(
        success=True,
        message="Transaksi berhasil diperbarui."
    )


# =====================================================
# DELETE TRANSACTION
# =====================================================

@router.delete(
    "/{transaction_id}",
    response_model=TransactionActionResponse
)
def delete_transaction_data(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    TransactionService.remove_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user["user_id"]
    )

    return TransactionActionResponse(
        success=True,
        message="Transaksi berhasil dihapus."
    )


# =====================================================
# IMPORT TRANSACTIONS
# =====================================================

@router.post(
    "/import",
    response_model=TransactionActionResponse
)
async def import_transactions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    try:

        content = await file.read()

        if file.filename.endswith(".csv"):

            raw_df = pd.read_csv(
                BytesIO(content)
            )

        elif (
            file.filename.endswith(".xlsx")
            or file.filename.endswith(".xls")
        ):

            raw_df = pd.read_excel(
                BytesIO(content)
            )

        else:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Format file harus "
                    "CSV atau Excel."
                )
            )

        cleaned_df = (
            auto_clean_financial_file(
                raw_df
            )
        )

        TransactionService.import_transactions(
            db=db,
            user_id=current_user["user_id"],
            imported_df=cleaned_df
        )

        return TransactionActionResponse(
            success=True,
            message=(
                f"{len(cleaned_df)} transaksi "
                f"berhasil diimport."
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )