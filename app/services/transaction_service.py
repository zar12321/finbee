# app/services/transaction_service.py

from sqlalchemy.orm import Session

from app.database.db import (
    load_transactions,
    load_categories,
    insert_transaction,
    insert_imported_transactions,
    update_transaction,
    delete_transaction, 
    get_filter_options, 
    filter_transactions, 
    get_transaction_by_id
)

from utils.validation import (
    validate_amount
)

from core.constants import (
    SUPPORTED_TRANSACTION_TYPES
)


class TransactionService:
    @staticmethod
    def get_transaction_by_id(
        db: Session,
        transaction_id: int,
        user_id: int
    ):
        return get_transaction_by_id(
            db=db,
            transaction_id=transaction_id,
            user_id=user_id
        )

    @staticmethod
    def get_transactions(
        db: Session,
        user_id: int
    ):

        return load_transactions(
            db=db,
            user_id=user_id
        )

    @staticmethod
    def get_categories(
        db: Session
    ):

        return load_categories(
            db=db
        )

    @staticmethod
    def create_transaction(
        db: Session,
        user_id: int,
        category_id: int,
        tanggal_transaksi,
        transaction_type: str,
        tujuan_transaksi: str,
        keterangan: str,
        payment_method: str,
        amount: float,
        source: str = "manual",
        raw_category: str | None = None
    ):

        if transaction_type not in SUPPORTED_TRANSACTION_TYPES:
            raise ValueError(
                "Jenis transaksi tidak valid."
            )

        valid_amount, message = validate_amount(
            amount
        )

        if not valid_amount:
            raise ValueError(message)

        insert_transaction(
            db=db,
            user_id=user_id,
            category_id=category_id,
            tanggal_transaksi=tanggal_transaksi,
            transaction_type=transaction_type,
            tujuan_transaksi=tujuan_transaksi,
            keterangan=keterangan,
            payment_method=payment_method,
            amount=amount,
            source=source,
            raw_category=raw_category
        )

        return True

    @staticmethod
    def import_transactions(
        db: Session,
        user_id: int,
        imported_df
    ):

        if imported_df is None:
            raise ValueError(
                "Data import tidak ditemukan."
            )

        if imported_df.empty:
            raise ValueError(
                "File transaksi kosong."
            )

        insert_imported_transactions(
            db=db,
            user_id=user_id,
            imported_df=imported_df
        )

        return True

    @staticmethod
    def edit_transaction(
        db: Session,
        transaction_id: int,
        user_id: int,
        category_id: int,
        tanggal_transaksi,
        transaction_type: str,
        tujuan_transaksi: str,
        keterangan: str,
        payment_method: str,
        amount: float,
        raw_category: str | None = None
    ):

        # ambil transaction lama
        current = get_transaction_by_id(
            db=db,
            transaction_id=transaction_id,
            user_id=user_id
        )

        if not current:
            raise ValueError(
                "Transaksi tidak ditemukan."
            )

        # fallback jika frontend kirim kosong
        if not transaction_type:
            transaction_type = current["transaction_type"]

        if not raw_category:
            raw_category = current["raw_category"]

        print("FINAL TYPE =", repr(transaction_type))
        print("FINAL RAW  =", repr(raw_category))

        if transaction_type not in SUPPORTED_TRANSACTION_TYPES:
            raise ValueError(
                f"Jenis transaksi tidak valid: {repr(transaction_type)}"
            )

        valid_amount, message = validate_amount(amount)

        if not valid_amount:
            raise ValueError(message)

        affected_rows = update_transaction(
            db=db,
            transaction_id=transaction_id,
            user_id=user_id,
            category_id=category_id,
            tanggal_transaksi=tanggal_transaksi,
            transaction_type=transaction_type,
            tujuan_transaksi=tujuan_transaksi,
            keterangan=keterangan,
            payment_method=payment_method,
            amount=amount,
            raw_category=raw_category
        )

        if affected_rows == 0:
            raise ValueError(
                "Transaksi tidak ditemukan."
            )

        return True

    @staticmethod
    def remove_transaction(
        db: Session,
        transaction_id: int,
        user_id: int
    ):

        affected_rows = delete_transaction(
            db=db,
            transaction_id=transaction_id,
            user_id=user_id
        )

        if affected_rows == 0:
            raise ValueError(
                "Transaksi tidak ditemukan."
            )

        return True


    # =====================================================
    # FILTER OPTIONS
    # =====================================================
    @staticmethod
    def get_filters(
        db: Session,
        user_id: int
    ):

        return get_filter_options(
            db=db,
            user_id=user_id
        )

    # =====================================================
    # FILTER TRANSACTIONS
    # =====================================================
    @staticmethod
    def filter_transactions(
        db: Session,
        user_id: int,
        period: str | None = None,
        month: int | None = None, 
        year: int | None = None, 
        category: str | None = None,
        subcategory_id: int | None = None,
        payment_method: str | None = None,
        tujuan: str | None = None,
        keterangan: str | None = None
    ):

        return filter_transactions(
            db=db,
            user_id=user_id,
            period=period,
            month=month, 
            year=year, 
            category=category,
            subcategory_id=subcategory_id,
            payment_method=payment_method,
            tujuan=tujuan,
            keterangan=keterangan
        )