from typing import List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator, ConfigDict

from core.dependencies import get_current_user, require_permission, get_service
from service.wallet import WalletService
from model.user import UserModel
from schemas.housekeeping import WalletSchema, TransactionSchema, RechargeSchema

from decimal import Decimal



router = APIRouter(prefix='/api/wallet', tags=['wallet'])


@router.get('/', response_model=WalletSchema)
def get_wallet(
    current_user: UserModel = Depends(require_permission()),
    service: WalletService = Depends(get_service(WalletService))
):
    """Get the wallet details for the current user.

    Args:
        current_user: Authenticated user.
        service: Injected WalletService instance.

    Returns:
        WalletSchema with balance and frozen_balance.
    """
    wallet = service.get_wallet(current_user.id)
    return wallet


@router.post('/recharge')
def recharge(
    data: RechargeSchema,
    current_user: UserModel = Depends(require_permission()),
    service: WalletService = Depends(get_service(WalletService))
):
    """Recharge the current user's wallet with a specified amount.

    Args:
        data: Recharge details including the amount.
        current_user: Authenticated user.
        service: Injected WalletService instance.

    Returns:
        dict with success status or error detail.
    """
    result = service.recharge(current_user.id, data.amount)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result


@router.get('/transactions', response_model=List[TransactionSchema])
def get_transactions(
    current_user: UserModel = Depends(require_permission()),
    service: WalletService = Depends(get_service(WalletService))
):
    """Get all transactions for the current user's wallet.

    Args:
        current_user: Authenticated user.
        service: Injected WalletService instance.

    Returns:
        List of TransactionSchema objects.
    """
    transactions = service.get_transactions(current_user.id)
    return transactions


@router.post('/pay/{order_id}')
def pay_order(
    order_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: WalletService = Depends(get_service(WalletService))
):
    """Pay for a service order using wallet balance.

    Args:
        order_id: The service order ID to pay for.
        current_user: Authenticated user.
        service: Injected WalletService instance.

    Returns:
        dict with success status or error detail.
    """
    result = service.pay_order(current_user.id, order_id)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result


@router.post('/settle/{order_id}')
def settle_to_cleaner(
    order_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: WalletService = Depends(get_service(WalletService))
):
    """Settle payment from customer wallet to the assigned cleaner for an order.

    Args:
        order_id: The service order ID to settle.
        current_user: Authenticated user (admin/manager role expected).
        service: Injected WalletService instance.

    Returns:
        dict with success status or error detail.
    """
    result = service.settle_to_cleaner(current_user.id, order_id)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result


@router.get('/cleaner-earnings')
def get_cleaner_earnings(
    current_user: UserModel = Depends(require_permission()),
    service: WalletService = Depends(get_service(WalletService))
):
    """Get earnings summary for the current user (cleaner).

    Args:
        current_user: Authenticated user.
        service: Injected WalletService instance.

    Returns:
        dict with earnings data or error detail.
    """
    result = service.get_cleaner_earnings(current_user.id)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result
