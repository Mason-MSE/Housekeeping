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
    wallet = service.get_wallet(current_user.id)
    return wallet


@router.post('/recharge')
def recharge(
    data: RechargeSchema,
    current_user: UserModel = Depends(require_permission()),
    service: WalletService = Depends(get_service(WalletService))
):
    result = service.recharge(current_user.id, data.amount)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result


@router.get('/transactions', response_model=List[TransactionSchema])
def get_transactions(
    current_user: UserModel = Depends(require_permission()),
    service: WalletService = Depends(get_service(WalletService))
):
    transactions = service.get_transactions(current_user.id)
    return transactions


@router.post('/pay/{order_id}')
def pay_order(
    order_id: int,
    current_user: UserModel = Depends(require_permission()),
    service: WalletService = Depends(get_service(WalletService))
):
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
    result = service.settle_to_cleaner(current_user.id, order_id)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result


@router.get('/cleaner-earnings')
def get_cleaner_earnings(
    current_user: UserModel = Depends(require_permission()),
    service: WalletService = Depends(get_service(WalletService))
):
    result = service.get_cleaner_earnings(current_user.id)

    if "error" in result:
        raise HTTPException(status_code=result["status_code"], detail=result["error"])

    return result
