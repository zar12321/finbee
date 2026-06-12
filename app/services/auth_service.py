from sqlalchemy.orm import Session
import re

from app.database.db import (
    register_user,
    login_user_by_identifier,
    reset_user_password,
    check_password
)

from utils.validation import (
    validate_name,
    validate_email,
    validate_username,
    validate_password,
    validate_confirm_password
)


class AuthService:

    @staticmethod
    def register(
        db: Session,
        nama: str,
        login_identifier: str,
        login_type: str,
        password: str,
        confirm_password: str,
        umur: int,
        pekerjaan: str
    ):

        valid_name, message = validate_name(nama)
        if not valid_name:
            raise ValueError(message)

        if login_type.lower() == "email":
            valid_login, message = validate_email(
                login_identifier
            )
        else:
            valid_login, message = validate_username(
                login_identifier
            )

        if not valid_login:
            raise ValueError(message)

        valid_password, message = (
            validate_password(password)
        )

        if not valid_password:
            raise ValueError(message)

        valid_confirm, message = (
            validate_confirm_password(
                password,
                confirm_password
            )
        )

        if pekerjaan:
            if not re.match(r"^[A-Za-z\s]+$", pekerjaan):
                raise ValueError("Pekerjaan hanya boleh berisi huruf")
                

        if not valid_confirm:
            raise ValueError(message)

        return register_user(
            db=db,
            nama=nama,
            login_identifier=login_identifier,
            login_type=login_type,
            password=password,
            umur=umur,
            pekerjaan=pekerjaan
        )

    @staticmethod
    def login(
        db: Session,
        login_identifier: str,
        password: str
    ):

        user = login_user_by_identifier(
            db=db,
            login_identifier=login_identifier
        )

        if user is None:
            raise ValueError(
                "Username/email tidak ditemukan."
            )

        if not check_password(
            password,
            user.password_hash
        ):
            raise ValueError(
                "Password salah."
            )

        return user

    @staticmethod
    def reset_password(
        db: Session,
        login_identifier: str,
        new_password: str,
        confirm_password: str
    ):

        valid_password, message = (
            validate_password(
                new_password
            )
        )

        if not valid_password:
            raise ValueError(message)

        valid_confirm, message = (
            validate_confirm_password(
                new_password,
                confirm_password
            )
        )

        if not valid_confirm:
            raise ValueError(message)

        affected_rows = reset_user_password(
            db=db,
            login_identifier=login_identifier,
            new_password=new_password
        )

        if affected_rows == 0:
            raise ValueError(
                "User tidak ditemukan."
            )

        return True

    @staticmethod
    def logout():

        return True