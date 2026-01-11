from abc import ABC, abstractmethod
from .dto import PayOrderRequest, PayOrderResponse


class PayOrderUseCase(ABC):
    """Интерфейс Use Case оплаты заказа"""
    
    @abstractmethod
    def execute(self, request: PayOrderRequest) -> PayOrderResponse:
        """Выполнение оплаты заказа"""
        pass
