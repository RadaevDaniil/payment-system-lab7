import pytest
from decimal import Decimal
from src.domain.entities import Order, OrderStatus
from src.domain.value_objects import Money
from src.application.use_cases import PayOrderUseCaseImpl
from src.application.dto import PayOrderRequest
from src.infrastructure.repositories.in_memory_order_repository import InMemoryOrderRepository
from src.infrastructure.payment_gateways.fake_payment_gateway import FakePaymentGateway


class TestPayOrderUseCase:
    """Тесты для Use Case оплаты заказа"""
    
    @pytest.fixture
    def order_repository(self):
        """Фикстура репозитория заказов"""
        return InMemoryOrderRepository()
    
    @pytest.fixture
    def payment_gateway(self):
        """Фикстура платежного шлюза"""
        return FakePaymentGateway()
    
    @pytest.fixture
    def use_case(self, order_repository, payment_gateway):
        """Фикстура Use Case"""
        return PayOrderUseCaseImpl(order_repository, payment_gateway)
    
    def test_successful_payment(self, order_repository, payment_gateway, use_case):
        """Тест успешной оплаты корректного заказа"""
        # Создаем заказ
        order = Order(id="order_1", customer_id="cust_1")
        order.add_line("prod_1", "Product 1", 2, Money(Decimal('10.00')))
        order_repository.save(order)
        
        # Выполняем оплату
        request = PayOrderRequest(order_id="order_1")
        response = use_case.execute(request)
        
        # Проверяем результат
        assert response.success is True
        assert response.order_id == "order_1"
        assert response.amount_paid == "USD 20.00"
        assert response.error_message is None
        
        # Проверяем, что заказ сохранен с правильным статусом
        saved_order = order_repository.get_by_id("order_1")
        assert saved_order.status == OrderStatus.PAID
        
        # Проверяем, что платежный шлюз был вызван
        assert payment_gateway.get_charges_count() == 1
    
    def test_payment_empty_order(self, order_repository, payment_gateway, use_case):
        """Тест ошибки при оплате пустого заказа"""
        # Создаем пустой заказ
        order = Order(id="order_1", customer_id="cust_1")
        order_repository.save(order)
        
        # Пытаемся оплатить
        request = PayOrderRequest(order_id="order_1")
        response = use_case.execute(request)
        
        # Проверяем результат
        assert response.success is False
        assert "Cannot pay empty order" in response.error_message
        
        # Проверяем, что платежный шлюз не был вызван
        assert payment_gateway.get_charges_count() == 0
    
    def test_payment_already_paid_order(self, order_repository, payment_gateway, use_case):
        """Тест ошибки при повторной оплате"""
        # Создаем и оплачиваем заказ
        order = Order(id="order_1", customer_id="cust_1")
        order.add_line("prod_1", "Product 1", 1, Money(Decimal('10.00')))
        order.pay()
        order_repository.save(order)
        
        # Пытаемся оплатить снова
        request = PayOrderRequest(order_id="order_1")
        response = use_case.execute(request)
        
        # Проверяем результат
        assert response.success is False
        assert "Order is already paid" in response.error_message
        
        # Проверяем, что платежный шлюз не был вызван
        assert payment_gateway.get_charges_count() == 0
    
    def test_order_not_found(self, order_repository, payment_gateway, use_case):
        """Тест оплаты несуществующего заказа"""
        request = PayOrderRequest(order_id="non_existent")
        response = use_case.execute(request)
        
        assert response.success is False
        assert "not found" in response.error_message
    
    def test_payment_gateway_failure(self, order_repository, payment_gateway, use_case):
        """Тест неудачной оплаты через платежный шлюз"""
        # Настраиваем платежный шлюз на отказ
        payment_gateway.fail_on_orders = {"order_1"}
        
        # Создаем заказ
        order = Order(id="order_1", customer_id="cust_1")
        order.add_line("prod_1", "Product 1", 1, Money(Decimal('10.00')))
        order_repository.save(order)
        
        # Пытаемся оплатить
        request = PayOrderRequest(order_id="order_1")
        response = use_case.execute(request)
        
        # Проверяем результат
        assert response.success is False
        assert "Payment failed" in response.error_message
        
        # Проверяем, что заказ НЕ был оплачен (сохранился CREATED статус)
        saved_order = order_repository.get_by_id("order_1")
        assert saved_order.status == OrderStatus.CREATED
    
    def test_cannot_modify_order_after_payment(self, order_repository, payment_gateway, use_case):
        """Тест невозможности изменения заказа после оплаты"""
        # Создаем и оплачиваем заказ
        order = Order(id="order_1", customer_id="cust_1")
        order.add_line("prod_1", "Product 1", 1, Money(Decimal('10.00')))
        order_repository.save(order)
        
        # Оплачиваем заказ
        request = PayOrderRequest(order_id="order_1")
        response = use_case.execute(request)
        assert response.success is True
        
        # Пытаемся изменить оплаченный заказ
        saved_order = order_repository.get_by_id("order_1")
        
        with pytest.raises(Exception) as exc_info:
            saved_order.add_line("prod_2", "Product 2", 1, Money(Decimal('5.00')))
        
        assert "Cannot modify paid order" in str(exc_info.value)
    
    def test_correct_total_amount_calculation(self, order_repository, payment_gateway, use_case):
        """Тест корректного расчета итоговой суммы"""
        # Создаем заказ с несколькими линиями
        order = Order(id="order_1", customer_id="cust_1")
        order.add_line("prod_1", "Product 1", 2, Money(Decimal('15.50')))
        order.add_line("prod_2", "Product 2", 3, Money(Decimal('7.25')))
        order_repository.save(order)
        
        # Вычисляем ожидаемую сумму: (15.50 * 2) + (7.25 * 3) = 31.00 + 21.75 = 52.75
        expected_total = Money(Decimal('52.75'))
        assert order.total_amount == expected_total
        
        # Оплачиваем заказ
        request = PayOrderRequest(order_id="order_1")
        response = use_case.execute(request)
        
        # Проверяем, что сумма оплаты корректна
        assert response.success is True
        assert response.amount_paid == str(expected_total)
        
        # Проверяем, что в платежный шлюз передана правильная сумма
        assert payment_gateway.charges_log[0]['amount'] == expected_total
