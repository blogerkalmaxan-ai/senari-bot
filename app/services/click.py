"""Click Merchant API (Prepare / Complete) protocol.

Flow:
  1. Click calls /click/prepare  (action=0) -> we reserve and return merchant_prepare_id
  2. Click calls /click/complete (action=1) -> we mark paid and deliver

Signature (MD5):
  prepare:  click_trans_id + service_id + secret_key + merchant_trans_id
            + amount + action + sign_time
  complete: click_trans_id + service_id + secret_key + merchant_trans_id
            + merchant_prepare_id + amount + action + sign_time
"""
import hashlib

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Payment, PaymentStatus

# Click error codes
SUCCESS = 0
SIGN_CHECK_FAILED = -1
INCORRECT_AMOUNT = -2
ACTION_NOT_FOUND = -3
ALREADY_PAID = -4
USER_NOT_FOUND = -5
TRANSACTION_NOT_FOUND = -6
TRANSACTION_CANCELLED = -9


def _md5(*parts) -> str:
    return hashlib.md5("".join(str(p) for p in parts).encode()).hexdigest()


def check_prepare_sign(d: dict) -> bool:
    expected = _md5(
        d["click_trans_id"],
        d["service_id"],
        settings.click_secret_key,
        d["merchant_trans_id"],
        d["amount"],
        d["action"],
        d["sign_time"],
    )
    return expected == d.get("sign_string")


def check_complete_sign(d: dict) -> bool:
    expected = _md5(
        d["click_trans_id"],
        d["service_id"],
        settings.click_secret_key,
        d["merchant_trans_id"],
        d.get("merchant_prepare_id", ""),
        d["amount"],
        d["action"],
        d["sign_time"],
    )
    return expected == d.get("sign_string")


async def handle_prepare(session: AsyncSession, d: dict) -> dict:
    if not check_prepare_sign(d):
        return {"error": SIGN_CHECK_FAILED, "error_note": "Invalid sign"}

    # merchant_trans_id encodes our payment id
    payment = await session.get(Payment, int(d["merchant_trans_id"]))
    if not payment:
        return {"error": TRANSACTION_NOT_FOUND, "error_note": "Not found"}
    if abs(float(payment.amount) - float(d["amount"])) > 0.01:
        return {"error": INCORRECT_AMOUNT, "error_note": "Bad amount"}

    payment.provider_charge_id = str(d["click_trans_id"])
    await session.commit()
    return {
        "click_trans_id": d["click_trans_id"],
        "merchant_trans_id": d["merchant_trans_id"],
        "merchant_prepare_id": payment.id,
        "error": SUCCESS,
        "error_note": "Success",
    }


async def handle_complete(session: AsyncSession, d: dict) -> dict:
    if not check_complete_sign(d):
        return {"error": SIGN_CHECK_FAILED, "error_note": "Invalid sign"}

    payment = await session.get(Payment, int(d["merchant_trans_id"]))
    if not payment:
        return {"error": TRANSACTION_NOT_FOUND, "error_note": "Not found"}
    if payment.status == PaymentStatus.paid:
        return {
            "click_trans_id": d["click_trans_id"],
            "merchant_trans_id": d["merchant_trans_id"],
            "merchant_confirm_id": payment.id,
            "error": SUCCESS,
            "error_note": "Already paid",
        }
    if int(d.get("error", 0)) < 0:
        payment.status = PaymentStatus.failed
        await session.commit()
        return {"error": TRANSACTION_CANCELLED, "error_note": "Cancelled"}

    payment.status = PaymentStatus.paid
    await session.commit()
    return {
        "click_trans_id": d["click_trans_id"],
        "merchant_trans_id": d["merchant_trans_id"],
        "merchant_confirm_id": payment.id,
        "error": SUCCESS,
        "error_note": "Success",
    }
