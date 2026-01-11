from decimal import Decimal
from typing import Set
from domain.value_objects import Money
from domain.interfaces import PaymentGateway


class FakePaymentGateway(PaymentGateway):
    """Fake реализация платежного шлюза"""
    
    def __init__(self, fail_on_orders: Set[str] = None):
        """
        Args:
            fail_on_orders: Множество ID заказов, для которых платеж должен завершиться неудачей
        """
        self.fail_on_orders = fail_on_orders or set()
        self.charges_log = []
    
    def charge(self, order_id: str, amount: Money) -> bool:
        """Выполнение платежа"""
        self.charges_log.append({
            'order_id': order_id,
            'amount': amount,
            'success': order_id not in self.fail_on_orders
        })
        
        return order_id not in self.fail_on_orders
    
    def get_charges_count(self) -> int:
        """Получение количества выполненных платежей"""
        return len(self.charges_log)
    
    def clear_log(self):
        """Очистка лога платежей"""
        self.charges_log.clear()
