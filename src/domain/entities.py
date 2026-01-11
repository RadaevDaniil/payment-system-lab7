from dataclasses import dataclass, field
from typing import List, Optional
from decimal import Decimal
from enum import Enum
from .value_objects import Money
from .exceptions import (
    EmptyOrderException, 
    OrderAlreadyPaidException, 
    OrderModificationException
)


class OrderStatus(Enum):
    """Статусы заказа"""
    CREATED = "created"
    PAID = "paid"
    CANCELLED = "cancelled"


@dataclass
class OrderLine:
    """Линия заказа - часть агрегата Order"""
    product_id: str
    product_name: str
    quantity: int
    unit_price: Money
    
    @property
    def total_price(self) -> Money:
        return self.unit_price * self.quantity


@dataclass
class Order:
    """Агрегат Order - корневая сущность"""
    id: str
    customer_id: str
    lines: List[OrderLine] = field(default_factory=list)
    status: OrderStatus = OrderStatus.CREATED
    
    def add_line(self, product_id: str, product_name: str, quantity: int, unit_price: Money):
        """Добавление линии в заказ"""
        if self.status == OrderStatus.PAID:
            raise OrderModificationException("Cannot modify paid order")
        
        self.lines.append(OrderLine(
            product_id=product_id,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price
        ))
    
    def remove_line(self, product_id: str):
        """Удаление линии из заказа"""
        if self.status == OrderStatus.PAID:
            raise OrderModificationException("Cannot modify paid order")
        
        self.lines = [line for line in self.lines if line.product_id != product_id]
    
    @property
    def total_amount(self) -> Money:
        """Расчет общей суммы заказа"""
        if not self.lines:
            return Money(Decimal('0'))
        
        total = Money(Decimal('0'))
        for line in self.lines:
            total = total + line.total_price
        return total
    
    def pay(self):
        """Оплата заказа"""
        if not self.lines:
            raise EmptyOrderException("Cannot pay empty order")
        
        if self.status == OrderStatus.PAID:
            raise OrderAlreadyPaidException("Order is already paid")
        
        self.status = OrderStatus.PAID
    
    def is_paid(self) -> bool:
        """Проверка, оплачен ли заказ"""
        return self.status == OrderStatus.PAID
    
    def __str__(self) -> str:
        return f"Order {self.id} - {self.status.value} - Total: {self.total_amount}"
