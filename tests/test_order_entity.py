import pytest
from decimal import Decimal
from src.domain.entities import Order, OrderLine, OrderStatus
from src.domain.value_objects import Money
from src.domain.exceptions import (
    EmptyOrderException, 
    OrderAlreadyPaidException, 
    OrderModificationException
)


class TestOrderEntity:
    """Тесты для сущности Order"""
    
    def test_create_order(self):
        """Тест создания заказа"""
        order = Order(id="123", customer_id="cust_1")
        
        assert order.id == "123"
        assert order.customer_id == "cust_1"
        assert order.status == OrderStatus.CREATED
        assert len(order.lines) == 0
        assert order.total_amount == Money(Decimal('0'))
    
    def test_add_line_to_order(self):
        """Тест добавления линии в заказ"""
        order = Order(id="123", customer_id="cust_1")
        unit_price = Money(Decimal('10.00'))
        
        order.add_line("prod_1", "Product 1", 2, unit_price)
        
        assert len(order.lines) == 1
        assert order.lines[0].product_id == "prod_1"
        assert order.lines[0].quantity == 2
        assert order.lines[0].total_price == Money(Decimal('20.00'))
        assert order.total_amount == Money(Decimal('20.00'))
    
    def test_total_amount_calculation(self):
        """Тест расчета общей суммы заказа"""
        order = Order(id="123", customer_id="cust_1")
        
        order.add_line("prod_1", "Product 1", 1, Money(Decimal('10.00')))
        order.add_line("prod_2", "Product 2", 3, Money(Decimal('5.00')))
        
        # 10.00 + (5.00 * 3) = 25.00
        assert order.total_amount == Money(Decimal('25.00'))
    
    def test_pay_order_success(self):
        """Тест успешной оплаты заказа"""
        order = Order(id="123", customer_id="cust_1")
        order.add_line("prod_1", "Product 1", 1, Money(Decimal('10.00')))
        
        order.pay()
        
        assert order.status == OrderStatus.PAID
        assert order.is_paid() is True
    
    def test_pay_empty_order_raises_exception(self):
        """Тест оплаты пустого заказа вызывает исключение"""
        order = Order(id="123", customer_id="cust_1")
        
        with pytest.raises(EmptyOrderException) as exc_info:
            order.pay()
        
        assert "Cannot pay empty order" in str(exc_info.value)
    
    def test_pay_already_paid_order_raises_exception(self):
        """Тест повторной оплаты вызывает исключение"""
        order = Order(id="123", customer_id="cust_1")
        order.add_line("prod_1", "Product 1", 1, Money(Decimal('10.00')))
        
        # Первая оплата
        order.pay()
        
        # Вторая оплата должна вызвать исключение
        with pytest.raises(OrderAlreadyPaidException) as exc_info:
            order.pay()
        
        assert "Order is already paid" in str(exc_info.value)
    
    def test_cannot_modify_paid_order(self):
        """Тест невозможности изменения оплаченного заказа"""
        order = Order(id="123", customer_id="cust_1")
        order.add_line("prod_1", "Product 1", 1, Money(Decimal('10.00')))
        order.pay()
        
        # Попытка добавления линии в оплаченный заказ
        with pytest.raises(OrderModificationException) as exc_info:
            order.add_line("prod_2", "Product 2", 1, Money(Decimal('5.00')))
        
        assert "Cannot modify paid order" in str(exc_info.value)
        
        # Попытка удаления линии из оплаченного заказа
        with pytest.raises(OrderModificationException) as exc_info:
            order.remove_line("prod_1")
    
    def test_remove_line_from_order(self):
        """Тест удаления линии из заказа"""
        order = Order(id="123", customer_id="cust_1")
        order.add_line("prod_1", "Product 1", 2, Money(Decimal('10.00')))
        order.add_line("prod_2", "Product 2", 1, Money(Decimal('5.00')))
        
        assert len(order.lines) == 2
        assert order.total_amount == Money(Decimal('25.00'))
        
        order.remove_line("prod_1")
        
        assert len(order.lines) == 1
        assert order.lines[0].product_id == "prod_2"
        assert order.total_amount == Money(Decimal('5.00'))


class TestMoneyValueObject:
    """Тесты для Value Object Money"""
    
    def test_money_creation(self):
        """Тест создания Money"""
        money = Money(Decimal('100.50'), "USD")
        
        assert money.amount == Decimal('100.50')
        assert money.currency == "USD"
    
    def test_money_addition(self):
        """Тест сложения Money"""
        money1 = Money(Decimal('100.00'), "USD")
        money2 = Money(Decimal('50.50'), "USD")
        
        result = money1 + money2
        
        assert result.amount == Decimal('150.50')
        assert result.currency == "USD"
    
    def test_money_multiplication(self):
        """Тест умножения Money"""
        money = Money(Decimal('10.00'), "USD")
        
        result = money * 3
        
        assert result.amount == Decimal('30.00')
    
    def test_money_from_float(self):
        """Тест создания Money из float"""
        money = Money.from_float(100.50, "USD")
        
        assert money.amount == Decimal('100.50')
        assert money.currency == "USD"
