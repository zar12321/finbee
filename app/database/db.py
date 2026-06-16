# app/database/db.py

from sqlalchemy import text
from sqlalchemy.orm import Session

import pandas as pd

import bcrypt

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

    print("PARAMS =", params)

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
# GET TRANSACTIONS BY USER ID
# =====================================================

def get_transactions_by_user_id(
    db: Session,
    user_id: int
):

    return load_transactions(
        db=db,
        user_id=user_id
    )

# =====================================================
# UPDATE TRANSACTION
# =====================================================

def update_transaction(
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

    result = db.execute(
        text("""
            UPDATE transactions
            SET
                category_id = :category_id,
                tanggal_transaksi = :tanggal_transaksi,
                transaction_type = :transaction_type,
                tujuan_transaksi = :tujuan_transaksi,
                keterangan = :keterangan,
                payment_method = :payment_method,
                amount = :amount,
                raw_category = :raw_category
            WHERE transaction_id = :transaction_id
            AND user_id = :user_id
        """),
        {
            "transaction_id": transaction_id,
            "user_id": user_id,
            "category_id": category_id,
            "tanggal_transaksi": tanggal_transaksi,
            "transaction_type": transaction_type,
            "tujuan_transaksi": tujuan_transaksi,
            "keterangan": keterangan,
            "payment_method": payment_method,
            "amount": amount,
            "raw_category": raw_category
        }
    )

    db.commit()

    return result.rowcount

# =====================================================
# IMPORT TRANSACTIONS
# =====================================================
def insert_imported_transactions(
    db: Session,
    user_id: int,
    imported_df
):

    categories_df = load_categories(db)

    category_map = dict(
        zip(
            categories_df["category_name"],
            categories_df["category_id"]
        )
    )

    # =========================
    # HAPUS DUPLIKAT DALAM FILE
    # =========================

    imported_df = imported_df.drop_duplicates(
        subset=[
            "tanggal_transaksi",
            "transaction_type",
            "category_name",
            "tujuan_transaksi",
            "payment_method",
            "amount"
        ]
    )

    # =========================
    # AMBIL TRANSAKSI USER
    # =========================

    existing_transactions = db.execute(
        text("""
            SELECT
                tanggal_transaksi,
                transaction_type,
                category_id,
                tujuan_transaksi,
                payment_method,
                amount
            FROM transactions
            WHERE user_id = :user_id
        """),
        {
            "user_id": user_id
        }
    ).fetchall()

    existing_keys = {
        (
            str(row.tanggal_transaksi),
            row.transaction_type,
            row.category_id,
            row.tujuan_transaksi,
            row.payment_method,
            float(row.amount)
        )
        for row in existing_transactions
    }

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

    inserted_count = 0
    skipped_count = 0

    for _, row in imported_df.iterrows():

        category_name = str(
            row["category_name"]
        ).strip()

        category_id = category_map.get(
            category_name
        )

        if category_id is None:

            category_id = category_map.get(
                "Other"
            )

        transaction_key = (
            str(row["tanggal_transaksi"]),
            row["transaction_type"],
            category_id,
            row["tujuan_transaksi"],
            row["payment_method"],
            float(row["amount"])
        )

        # =========================
        # CEK DUPLIKAT DATABASE
        # =========================

        if transaction_key in existing_keys:

            skipped_count += 1
            continue

        db.execute(
            query,
            {
                "user_id": user_id,
                "category_id": category_id,
                "tanggal_transaksi": row["tanggal_transaksi"],
                "transaction_type": row["transaction_type"],
                "tujuan_transaksi": row["tujuan_transaksi"],
                "keterangan": row["keterangan"],
                "payment_method": row["payment_method"],
                "amount": float(row["amount"]),
                "source": "import_file",
                "raw_category": row.get(
                    "raw_category",
                    category_name
                )
            }
        )

        existing_keys.add(
            transaction_key
        )

        inserted_count += 1

    db.commit()

    return {
        "inserted_count": inserted_count,
        "skipped_count": skipped_count
    }

# =====================================================
# PASSWORD
# =====================================================

def hash_password(
    password: str
):

    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


def check_password(
    password: str,
    password_hash: str
):

    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8")
    )

# =====================================================
# REGISTER USER
# =====================================================

def register_user(
    db: Session,
    nama: str,
    login_identifier: str,
    login_type: str,
    password: str,
    umur: int,
    pekerjaan: str
):

    password_hash = hash_password(
        password
    )

    result = db.execute(
        text("""
            INSERT INTO users
            (
                nama,
                login_identifier,
                login_type,
                password_hash,
                umur,
                pekerjaan
            )
            VALUES
            (
                :nama,
                :login_identifier,
                :login_type,
                :password_hash,
                :umur,
                :pekerjaan
            )
            RETURNING user_id
        """),
        {
            "nama": nama,
            "login_identifier": login_identifier,
            "login_type": login_type,
            "password_hash": password_hash,
            "umur": umur,
            "pekerjaan": pekerjaan
        }
    )

    db.commit()

    return result.fetchone()

# =====================================================
# LOGIN USER
# =====================================================

def login_user_by_identifier(
    db: Session,
    login_identifier: str
):

    result = db.execute(
        text("""
            SELECT
                user_id,
                nama,
                login_identifier,
                pekerjaan,
                login_type,
                password_hash, 
             profile_photo
            FROM users
            WHERE login_identifier = :login_identifier
            LIMIT 1
        """),
        {
            "login_identifier":
                login_identifier
        }
    )

    return result.fetchone()

# =====================================================
# RESET PASSWORD
# =====================================================

def reset_user_password(
    db: Session,
    login_identifier: str,
    new_password: str
):

    password_hash = hash_password(
        new_password
    )

    result = db.execute(
        text("""
            UPDATE users
            SET password_hash = :password_hash
            WHERE login_identifier = :login_identifier
        """),
        {
            "login_identifier": login_identifier,
            "password_hash": password_hash
        }
    )

    db.commit()

    return result.rowcount

# =====================================================
# GET USER BY ID
# =====================================================

def get_user_by_id(
    db: Session,
    user_id: int
):

    result = db.execute(
        text("""
            SELECT
                user_id,
                nama,
                login_identifier,
                login_type,
                umur,
                pekerjaan,
                created_at, 
                profile_photo
            FROM users
            WHERE user_id = :user_id
            LIMIT 1
        """),
        {
            "user_id": user_id
        }
    )

    return result.fetchone()

# =====================================================
# UPDATE USER PROFILE
# =====================================================

def update_user_profile(
    db: Session,
    user_id: int,
    nama: str,
    login_identifier: str, 
    umur: int | None,
    pekerjaan: str | None
):

    db.execute(
        text("""
            UPDATE users
            SET
                nama = :nama,
                login_identifier =:login_identifier,
                umur = :umur,
                pekerjaan = :pekerjaan
            WHERE user_id = :user_id
        """),
        {
            "nama": nama,
            "login_identifier": login_identifier,
            "umur": umur,
            "pekerjaan": pekerjaan,
            "user_id": user_id
        }
    )

    db.commit()

# =====================================================
# UPDATE PROFILE PHOTO
# =====================================================
def update_profile_photo(
    db: Session, 
    user_id: int, 
    profile_photo: str
):
    result=db.execute(
        text("""
            update users
            set profile_photo = :profile_photo
            where user_id = :user_id
        """),
        {
            "profile_photo": profile_photo, 
            "user_id": user_id
        }    
    )

    print("updated", result.rowcount)

    db.commit()

# =====================================================
# LOAD MONTHLY PLAN
# =====================================================

def load_monthly_plan(
    db: Session,
    user_id: int,
    bulan: int,
    tahun: int
):

    result = db.execute(
        text("""
            SELECT
                plan_id,
                user_id,
                bulan,
                tahun,
                pemasukan_bulanan,
                target_bulanan
            FROM monthly_plans
            WHERE user_id = :user_id
            AND bulan = :bulan
            AND tahun = :tahun
            LIMIT 1
        """),
        {
            "user_id": user_id,
            "bulan": bulan,
            "tahun": tahun
        }
    )

    return result.fetchone()

# =====================================================
# SAVE MONTHLY PLAN
# =====================================================

def save_monthly_plan(
    db: Session,
    user_id: int,
    bulan: int,
    tahun: int,
    target_bulanan: float,
    pemasukan_bulanan: float = 0
):

    db.execute(
        text("""
            INSERT INTO monthly_plans
            (
                user_id,
                bulan,
                tahun,
                pemasukan_bulanan,
                target_bulanan
            )
            VALUES
            (
                :user_id,
                :bulan,
                :tahun,
                :pemasukan_bulanan,
                :target_bulanan
            )
            ON CONFLICT
            (
                user_id,
                bulan,
                tahun
            )
            DO UPDATE SET
                pemasukan_bulanan =
                    EXCLUDED.pemasukan_bulanan,
                target_bulanan =
                    EXCLUDED.target_bulanan,
                updated_at =
                    CURRENT_TIMESTAMP
        """),
        {
            "user_id": user_id,
            "bulan": bulan,
            "tahun": tahun,
            "pemasukan_bulanan": pemasukan_bulanan,
            "target_bulanan": target_bulanan
        }
    )

    db.commit()

# =====================================================
# FILTER OPTIONS
# =====================================================

def get_filter_options(
    db: Session,
    user_id: int
):
    categories = db.execute(
        text("""
            SELECT DISTINCT
                transaction_type
            FROM transactions
            WHERE user_id = :user_id
            ORDER BY transaction_type
        """),
        {
            "user_id": user_id
        }
    ).fetchall()

    PAYMENT_METHODS = [
        "Cash",
        "Bank BCA",
        "Bank BRI",
        "Bank BNI",
        "Bank Mandiri",
        "OVO",
        "GoPay",
        "DANA",
        "ShopeePay"
    ]

    subcategories = db.execute(
        text("""
            SELECT
                category_id,
                category_name
            FROM categories
            ORDER BY category_name
        """)
    ).fetchall()

    years = db.execute(
        text("""
            SELECT DISTINCT
                EXTRACT(
                    YEAR FROM tanggal_transaksi
                ) AS year
            FROM transactions
            WHERE user_id = :user_id
            ORDER BY year DESC
        """),
        {
            "user_id": user_id
        }
    ).fetchall()

    return {
        "categories": [
            row[0]
            for row in categories
        ],

        "payment_methods": PAYMENT_METHODS,

        "subcategories": [
            {
                "category_id": row[0],
                "category_name": row[1]
            }
            for row in subcategories
        ],

        "years": [
            int(row[0])
            for row in years
        ]
    }

# =====================================================
# FILTER TRANSACTIONS
# =====================================================

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
        WHERE t.user_id = :user_id
    """

    params = {
        "user_id": user_id
    }

    # =========================================
    # PERIODE
    # =========================================
    print("periode=", period)

    if period == "today":

        query += """
            AND DATE(t.tanggal_transaksi)
                = date(CURRENT_DATE + interval '1 day')
        """

    elif period == "yesterday":

        query += """
            AND DATE(t.tanggal_transaksi)
                = date(current_date)
        """

    elif period == "7days":

        query += """
            AND t.tanggal_transaksi >=
                date(CURRENT_DATE + interval '1 day' - INTERVAL '7 day')
            AND t.tanggal_transaksi <=
                date(CURRENT_DATE + interval '1 day')
        """

    elif period == "30days":

        query += """
            AND t.tanggal_transaksi >=
                date(CURRENT_DATE + interval '1 day' - INTERVAL '30 day')
            and t.tanggal_transaksi <=
                date(CURRENT_DATE + interval '1 day')
        """

    # =========================================
    # BULAN
    # =========================================

    if month:

        query += """
            AND EXTRACT(
                MONTH FROM t.tanggal_transaksi
            ) = :month
        """

        params["month"] = month


    # =========================================
    # TAHUN
    # =========================================

    if year:

        query += """
            AND EXTRACT(
                YEAR FROM t.tanggal_transaksi
            ) = :year
        """

        params["year"] = year

    # =========================================
    # KATEGORI
    # =========================================

    if category:

        query += """
            AND t.transaction_type = :category
        """

        params["category"] = category

    # =========================================
    # SUBKATEGORI
    # =========================================

    if subcategory_id:

        query += """
            AND t.category_id = :subcategory_id
        """

        params["subcategory_id"] = subcategory_id

    # =========================================
    # PAYMENT METHOD
    # =========================================

    if payment_method:

        query += """
            AND TRIM(
                LOWER(t.payment_method)
            ) =
            TRIM(
                LOWER(:payment_method)
            )
        """

        params["payment_method"] = payment_method

    # =========================================
    # TUJUAN TRANSAKSI
    # =========================================

    if tujuan:

        keywords = tujuan.split()

        for i, word in enumerate(keywords):

            key = f"tujuan_{i}"

            query += f"""
                AND LOWER(t.tujuan_transaksi)
                LIKE LOWER(:{key})
            """

            params[key] = f"%{word}%"

    # =========================================
    # KETERANGAN
    # =========================================

    if keterangan:

        keywords = keterangan.split()

        for i, word in enumerate(keywords):

            key = f"tujuan_{i}"

            query += f"""
                AND LOWER(t.keterangan)
                LIKE LOWER(:{key})
            """

            params[key] = f"%{word}%"

    # =========================================
    # ORDER
    # =========================================

    query += """
        ORDER BY
            t.tanggal_transaksi DESC,
            t.transaction_id DESC
    """

    print(query)
    print(params)

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

# =========================================
# GET TRANSACTION BY ID
# =========================================
def get_transaction_by_id(
    db: Session,
    transaction_id: int,
    user_id: int
):

    query = """
    SELECT
        t.transaction_id,
        t.tanggal_transaksi,
        t.raw_category,
        c.category_name,
        t.tujuan_transaksi,
        t.payment_method,
        t.transaction_type,
        t.amount,
        t.keterangan
    FROM transactions t
    LEFT JOIN categories c
        ON t.category_id = c.category_id
    WHERE
        t.transaction_id = :transaction_id
        AND t.user_id = :user_id
    """

    result = db.execute(
        text(query),
        {
            "transaction_id": transaction_id,
            "user_id": user_id
        }
    ).mappings().first()

    return dict(result) if result else {}