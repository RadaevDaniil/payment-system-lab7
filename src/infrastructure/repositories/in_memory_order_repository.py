from typing import Dict, Optional
from domain.entities import Order
from domain.interfaces import OrderRepository


class InMemoryOrderRepository(OrderRepository):
    """In-memory реализация репозитория заказов"""
    
    def __init__(self):
        self._orders: Dict[str, Order] = {}
    
    def get_by_id(self, order_id: str) -> Optional[Order]:
        """Получение заказа по ID"""
        return self._orders.get(order_id)
    
    def save(self, order: Order):
        """Сохранение заказа"""
        self._orders[order.id] = order
    
    def clear(self):
        """Очистка хранилища (для тестов)"""
        self._orders.clear()
