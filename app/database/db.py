# app/database/db.py

from sqlalchemy import text
from sqlalchemy.orm import Session

import pandas as pd


# =====================================================
# HEALTH CHECK
# =====================================================

def test_connection(db: Session):

    result = db.execute(
        text("SELECT 1 AS status")
    )

    return result.fetchone()


# =====================================================
# USERS
# =====================================================

def load_users(db: Session):

    query = text("""
        SELECT
            user_id,
            nama,
            login_identifier,
            login_type,
            umur,
            pekerjaan,
            created_at
        FROM users
        ORDER BY user_id
    """)

    result = db.execute(query)

    return pd.DataFrame(
        result.fetchall(),
        columns=result.keys()
    )


# =====================================================
# CATEGORIES
# =====================================================

def load_categories(db: Session):

    query = text("""
        SELECT
            category_id,
            category_name,
            category_type
        FROM categories
        ORDER BY category_type,
                 category_name
    """)

    result = db.execute(query)

    return pd.DataFrame(
        result.fetchall(),
        columns=result.keys()
    )


# =====================================================
# TRANSACTIONS
# =====================================================

def load_transactions(
    db: Session,
    user_id: int | None = None
):

    query = """
        SELECT
            t.transaction_id,
            t.user_id,
            u.nama AS user_name,
            t.category_id,
            c.category_name,
            t.raw_category,
            t.import_id,
            t.tanggal_input,
            t.tanggal_transaksi,
            t.transaction_type,
            t.tujuan_transaksi,
            t.keterangan,
            t.payment_method,
            t.amount,
            t.source,
            t.created_at
        FROM transactions t
        JOIN users u
            ON t.user_id = u.user_id
        LEFT JOIN categories c
            ON t.category_id = c.category_id
    """

    params = {}

    if user_id is not None:

        query += """
            WHERE t.user_id = :user_id
        """

        params["user_id"] = user_id

    query += """
        ORDER BY
            t.tanggal_transaksi DESC
    """

    result = db.execute(
        text(query),
        params
    )

    df = pd.DataFrame(
        result.fetchall(),
        columns=result.keys()
    )

    if not df.empty:

        df["tanggal_transaksi"] = pd.to_datetime(
            df["tanggal_transaksi"]
        )

        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce"
        )

    return df


# =====================================================
# INSERT TRANSACTION
# =====================================================

def insert_transaction(
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

    query = text("""
        INSERT INTO transactions
        (
            user_id,
            category_id,
            tanggal_transaksi,
            transaction_type,
            tujuan_transaksi,
            keterangan,
            payment_method,
            amount,
            source,
            raw_category
        )
        VALUES
        (
            :user_id,
            :category_id,
            :tanggal_transaksi,
            :transaction_type,
            :tujuan_transaksi,
            :keterangan,
            :payment_method,
            :amount,
            :source,
            :raw_category
        )
    """)

    db.execute(
        query,
        {
            "user_id": user_id,
            "category_id": category_id,
            "tanggal_transaksi": tanggal_transaksi,
            "transaction_type": transaction_type,
            "tujuan_transaksi": tujuan_transaksi,
            "keterangan": keterangan,
            "payment_method": payment_method,
            "amount": amount,
            "source": source,
            "raw_category": raw_category
        }
    )

    db.commit()


# =====================================================
# DELETE TRANSACTION
# =====================================================

def delete_transaction(
    db: Session,
    transaction_id: int,
    user_id: int
):

    result = db.execute(
        text("""
            DELETE FROM transactions
            WHERE transaction_id = :transaction_id
            AND user_id = :user_id
        """),
        {
            "transaction_id": transaction_id,
            "user_id": user_id
        }
    )

    db.commit()

    return result.rowcount


# =====================================================
# DELETE ALL TRANSACTIONS
# =====================================================

def delete_all_transactions(
    db: Session,
    user_id: int
):

    result = db.execute(
        text("""
            DELETE FROM transactions
            WHERE user_id = :user_id
        """),
        {
            "user_id": user_id
        }
    )

    db.commit()

    return result.rowcount