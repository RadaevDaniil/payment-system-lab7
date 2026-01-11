import sys
import os

# Добавляем src в путь Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Тестирование импортов...")
    
    # Domain слой
    from domain.entities import Order, OrderLine, OrderStatus
    from domain.value_objects import Money
    from domain.exceptions import DomainException
    from domain.interfaces import OrderRepository, PaymentGateway
    print("✅ Domain слой импортирован")
    
    # Application слой
    from application.dto import PayOrderRequest, PayOrderResponse
    from application.interfaces import PayOrderUseCase
    from application.use_cases import PayOrderUseCaseImpl
    print("✅ Application слой импортирован")
    
    # Infrastructure слой
    from infrastructure.repositories.in_memory_order_repository import InMemoryOrderRepository
    from infrastructure.payment_gateways.fake_payment_gateway import FakePaymentGateway
    print("✅ Infrastructure слой импортирован")
    
    print("\n✅ Все импорты работают корректно!")
    
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
