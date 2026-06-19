from sqlalchemy import text
from sqlalchemy.orm import Session


# ==========================================
# SAVE CHAT HISTORY
# ==========================================

def save_chat_history(
    db: Session,
    user_id: int,
    role: str,
    message: str,
    provider: str,
    model_name: str
):

    db.execute(
        text("""
            INSERT INTO chat_history (
                user_id,
                role,
                message,
                provider,
                model_name
            )
            VALUES (
                :user_id,
                :role,
                :message,
                :provider,
                :model_name
            )
        """),
        {
            "user_id": user_id,
            "role": role,
            "message": message,
            "provider": provider,
            "model_name": model_name
        }
    )

    db.commit()

def get_chat_history(
    db: Session,
    user_id: int,
    limit: int = 5
):

    result = db.execute(
        text("""
            SELECT
                chat_id,
                role,
                message,
                provider,
                model_name,
                created_at
            FROM chat_history
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit
        """),
        {
            "user_id": user_id,
            "limit": limit
        }
    )

    rows = result.mappings().all()

    return [
        dict(row)
        for row in rows
    ]

def get_recent_chat_context(
    db: Session,
    user_id: int,
    limit: int = 10
):

    result = db.execute(
        text("""
            SELECT
                role,
                message
            FROM chat_history
            WHERE user_id = :user_id
            ORDER BY chat_id DESC
            LIMIT :limit
        """),
        {
            "user_id": user_id,
            "limit": limit
        }
    )

    rows = result.mappings().all()

    return list(
        reversed(rows)
    )

def clear_chat_history(
    db: Session,
    user_id: int
):

    db.execute(
        text("""
            DELETE
            FROM chat_history
            WHERE user_id = :user_id
        """),
        {
            "user_id": user_id
        }
    )

    db.commit()