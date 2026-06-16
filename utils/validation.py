import re

from core.constants import (
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    MAX_NAME_LENGTH,
    MAX_LOGIN_IDENTIFIER_LENGTH
)


def validate_name(
    name
) -> tuple[bool, str]:

    if not name:
        return False, "Nama wajib diisi."

    name = str(name).strip()

    if not name:
        return False, "Nama wajib diisi."

    if len(name) > MAX_NAME_LENGTH:
        return (
            False,
            f"Nama maksimal {MAX_NAME_LENGTH} karakter."
        )

    return True, ""



def validate_username(
    username
) -> tuple[bool, str]:

    if not username:
        return False, "Username wajib diisi."

    username = str(username).strip()

    if len(username) < 3:
        return (
            False,
            "Username minimal 3 karakter."
        )

    if len(username) > MAX_LOGIN_IDENTIFIER_LENGTH:
        return (
            False,
            f"Username maksimal "
            f"{MAX_LOGIN_IDENTIFIER_LENGTH} karakter."
        )

    return True, ""


def validate_password(
    password
) -> tuple[bool, str]:

    if not password:
        return False, "Password wajib diisi."

    password = str(password)

    if len(password) < MIN_PASSWORD_LENGTH:
        return (
            False,
            f"Password minimal "
            f"{MIN_PASSWORD_LENGTH} karakter."
        )

    if len(password) > MAX_PASSWORD_LENGTH:
        return (
            False,
            f"Password maksimal "
            f"{MAX_PASSWORD_LENGTH} karakter."
        )

    return True, ""


def validate_confirm_password(
    password,
    confirm_password
) -> tuple[bool, str]:

    if password != confirm_password:
        return (
            False,
            "Konfirmasi password tidak cocok."
        )

    return True, ""


def validate_age(
    age
) -> tuple[bool, str]:

    try:
        age = int(age)

    except (
        TypeError,
        ValueError
    ):
        return (
            False,
            "Umur harus berupa angka."
        )

    if age < 0:
        return (
            False,
            "Umur tidak valid."
        )

    if age > 120:
        return (
            False,
            "Umur tidak valid."
        )

    return True, ""


def validate_amount(
    amount
) -> tuple[bool, str]:

    try:
        amount = float(amount)

    except (
        TypeError,
        ValueError
    ):
        return (
            False,
            "Nominal harus berupa angka."
        )

    if amount <= 0:
        return (
            False,
            "Nominal harus lebih besar dari 0."
        )

    return True, ""


def validate_transaction_form(
    category_id,
    tanggal_transaksi,
    payment_method,
    amount
) -> tuple[bool, str]:

    if category_id is None:
        return (
            False,
            "Kategori wajib dipilih."
        )

    if tanggal_transaksi is None:
        return (
            False,
            "Tanggal transaksi wajib diisi."
        )

    if not payment_method:
        return (
            False,
            "Metode pembayaran wajib diisi."
        )

    is_valid, message = (
        validate_amount(amount)
    )

    if not is_valid:
        return (
            False,
            message
        )

    return True, ""


def validate_login_identifier(
    login_identifier,
    login_type
) -> tuple[bool, str]:

    if login_type == "Email":
        return validate_email(
            login_identifier
        )

    return validate_username(
        login_identifier
    )