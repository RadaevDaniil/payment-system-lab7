from abc import ABC, abstractmethod
from typing import Optional
from .entities import Order
from .value_objects import Money


class OrderRepository(ABC):
    """Интерфейс репозитория заказов"""
    
    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]:
        """Получение заказа по ID"""
        pass
    
    @abstractmethod
    def save(self, order: Order):
        """Сохранение заказа"""
        pass


class PaymentGateway(ABC):
    """Интерфейс платежного шлюза"""
    
    @abstractmethod
    def charge(self, order_id: str, amount: Money) -> bool:
        """Выполнение платежа"""
        pass
