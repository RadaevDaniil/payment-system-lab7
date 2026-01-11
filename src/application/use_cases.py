from typing import Optional
from decimal import Decimal
from .dto import PayOrderRequest, PayOrderResponse
from .interfaces import PayOrderUseCase
from ..domain.entities import Order, OrderStatus
from ..domain.interfaces import OrderRepository, PaymentGateway
from ..domain.exceptions import DomainException


class PayOrderUseCaseImpl(PayOrderUseCase):
    """Реализация Use Case оплаты заказа"""
    
    def __init__(self, order_repository: OrderRepository, payment_gateway: PaymentGateway):
        self.order_repository = order_repository
        self.payment_gateway = payment_gateway
    
    def execute(self, request: PayOrderRequest) -> PayOrderResponse:
        """Выполнение оплаты заказа"""
        try:
            # Загружаем заказ
            order: Optional[Order] = self.order_repository.get_by_id(request.order_id)
            
            if not order:
                return PayOrderResponse(
                    success=False,
                    order_id=request.order_id,
                    error_message=f"Order {request.order_id} not found"
                )
            
            # Сохраняем исходное состояние для возможного отката
            original_status = order.status
            
            try:
                # Выполняем доменную операцию оплаты
                order.pay()
                
                # Вызываем платежный шлюз
                payment_success = self.payment_gateway.charge(order.id, order.total_amount)
                
                if not payment_success:
                    # Откатываем статус заказа если платеж не прошел
                    order.status = original_status
                    return PayOrderResponse(
                        success=False,
                        order_id=order.id,
                        error_message="Payment failed"
                    )
                
                # Сохраняем заказ с новым статусом
                self.order_repository.save(order)
                
                return PayOrderResponse(
                    success=True,
                    order_id=order.id,
                    amount_paid=str(order.total_amount)
                )
                
            except Exception:
                # Если что-то пошло не так, откатываем изменения
                order.status = original_status
                raise
                
        except DomainException as e:
            return PayOrderResponse(
                success=False,
                order_id=request.order_id,
                error_message=str(e)
            )
        except Exception as e:
            return PayOrderResponse(
                success=False,
                order_id=request.order_id,
                error_message=f"Unexpected error: {str(e)}"
            )
