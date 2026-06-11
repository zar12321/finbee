from app.database.db import (
    load_transactions,
    load_categories,
    insert_transaction,
    insert_imported_transactions,
    update_transaction,
    delete_transactions
)

from utils.validation import validate_amount

from core.constants import (
    SUPPORTED_TRANSACTION_TYPES
)


class TransactionService:

    @staticmethod
    def get_transactions():

        return load_transactions()

    @staticmethod
    def get_categories():

        return load_categories()

    @staticmethod
    def create_transaction(
        user_id,
        category_id,
        tanggal_transaksi,
        transaction_type,
        tujuan_transaksi,
        keterangan,
        payment_method,
        amount,
        source="manual",
        raw_category=None
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
        user_id,
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
            user_id=user_id,
            imported_df=imported_df
        )

        return True

    @staticmethod
    def edit_transaction(
        transaction_id,
        user_id,
        category_id,
        tanggal_transaksi,
        transaction_type,
        tujuan_transaksi,
        keterangan,
        payment_method,
        amount,
        raw_category=None
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

        affected_rows = update_transaction(
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
        transaction_id,
        user_id
    ):

        affected_rows = delete_transactions(
            [transaction_id],
            user_id
        )

        if affected_rows == 0:
            raise ValueError(
                "Transaksi tidak ditemukan."
            )

        return True