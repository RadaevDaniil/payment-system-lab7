from dataclasses import dataclass
from typing import Optional


@dataclass
class PayOrderRequest:
    """DTO для запроса на оплату заказа"""
    order_id: str


@dataclass
class PayOrderResponse:
    """DTO для ответа на оплату заказа"""
    success: bool
    order_id: str
    error_message: Optional[str] = None
    amount_paid: Optional[str] = None
