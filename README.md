```markdown
# Система оплаты заказа - Лабораторная работа 7

Реализация системы оплаты заказа с использованием слоистой архитектуры и DDD-lite (Domain-Driven Design).

## 📋 Описание проекта

Проект представляет собой учебную реализацию системы обработки заказов с акцентом на чистой архитектуре, разделении ответственности и доменно-ориентированном дизайне. Система позволяет создавать заказы, добавлять товары, рассчитывать стоимость и выполнять оплату с соблюдением бизнес-правил.

## 🏗️ Архитектура проекта

Проект разделен на следующие слои в соответствии с принципами чистой архитектуры:

### 1. Domain (Доменный слой) - `src/domain/`
Ядро системы, содержащее бизнес-логику и правила:
- **Сущности (Entities)**: `Order`, `OrderLine`
- **Value Objects**: `Money` (неизменяемый объект-значение)
- **Перечисления (Enums)**: `OrderStatus`
- **Интерфейсы репозиториев**: `OrderRepository`, `PaymentGateway`
- **Доменные исключения**: `DomainException`, `EmptyOrderException`, `OrderAlreadyPaidException` и др.

### 2. Application (Слой приложения) - `src/application/`
Содержит use cases и координацию работы домена:
- **Use Cases**: `PayOrderUseCaseImpl` - основной сценарий оплаты заказа
- **DTO (Data Transfer Objects)**: `PayOrderRequest`, `PayOrderResponse`
- **Интерфейсы use cases**: `PayOrderUseCase`

### 3. Infrastructure (Инфраструктурный слой) - `src/infrastructure/`
Реализация внешних зависимостей и технических деталей:
- **Репозитории**: `InMemoryOrderRepository` - хранение в памяти
- **Платежные шлюзы**: `FakePaymentGateway` - заглушка для платежей

### 4. Tests (Тесты) - `tests/`
Полный набор модульных тестов:
- Тесты доменных сущностей и value objects
- Интеграционные тесты use cases
- Тесты бизнес-правил и инвариантов

## 📊 Доменные правила (инварианты)

Система гарантирует соблюдение следующих бизнес-правил:

1. **Нельзя оплатить пустой заказ** - заказ должен содержать хотя бы одну товарную позицию
2. **Нельзя оплатить заказ повторно** - один заказ может быть оплачен только один раз
3. **После оплаты нельзя менять строки заказа** - оплаченный заказ становится неизменяемым
4. **Итоговая сумма равна сумме строк** - автоматический расчет общей стоимости

## 🚀 Быстрый старт

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Запуск примера
```bash
python example.py
```

### Запуск тестов
```bash
# Все тесты
pytest tests/ -v

# Тесты с покрытием кода
pytest tests/ --cov=src --cov-report=html

# Конкретный тестовый файл
pytest tests/test_order_entity.py -v
pytest tests/test_pay_order_use_case.py -v
```

## 📖 Пример использования

```python
from decimal import Decimal
from src.domain.entities import Order
from src.domain.value_objects import Money
from src.application.use_cases import PayOrderUseCaseImpl
from src.application.dto import PayOrderRequest
from src.infrastructure.repositories.in_memory_order_repository import InMemoryOrderRepository
from src.infrastructure.payment_gateways.fake_payment_gateway import FakePaymentGateway

# 1. Инициализация компонентов
order_repo = InMemoryOrderRepository()
payment_gateway = FakePaymentGateway()
use_case = PayOrderUseCaseImpl(order_repo, payment_gateway)

# 2. Создание заказа
order = Order(id="order_1", customer_id="customer_1")
order.add_line("prod_1", "Ноутбук", 1, Money(Decimal("999.99")))
order.add_line("prod_2", "Мышь", 2, Money(Decimal("25.50")))
order_repo.save(order)

print(f"Создан заказ: {order}")
print(f"Общая сумма: {order.total_amount}")

# 3. Оплата заказа
request = PayOrderRequest(order_id="order_1")
response = use_case.execute(request)

if response.success:
    print(f"✅ Оплата успешна! Сумма: {response.amount_paid}")
else:
    print(f"❌ Ошибка: {response.error_message}")
```

## 🧪 Тестирование

Проект содержит комплексные тесты, проверяющие:

### Доменные сущности (`test_order_entity.py`)
- Создание заказа и добавление товаров
- Расчет общей суммы
- Оплата заказа (успешная и с ошибками)
- Проверка инвариантов (пустой заказ, повторная оплата)
- Value Object `Money` (сложение, умножение, валидация)

### Use Cases (`test_pay_order_use_case.py`)
- Успешная оплата корректного заказа
- Ошибка при оплате пустого заказа
- Ошибка при повторной оплате
- Неудача платежа через платежный шлюз
- Корректный расчет итоговой суммы

## 🏷️ Value Object: Money

Реализация паттерна Value Object для работы с денежными суммами:
- Неизменяемый (immutable) объект
- Автоматическая валидация (сумма не может быть отрицательной)
- Поддержка арифметических операций (сложение, умножение)
- Поддержка разных валют (с проверкой при операциях)
- Сериализация в строку

```python
# Создание денежной суммы
price = Money(Decimal("100.50"), "USD")
discount = Money(Decimal("20.00"), "USD")

# Арифметические операции
total = price + discount  # USD 120.50
quantity_price = price * 3  # USD 301.50
```

## 🔧 Принципы проектирования

### Dependency Inversion Principle (DIP)
- Высокоуровневые модули (Application) не зависят от низкоуровневых (Infrastructure)
- Оба зависят от абстракций (интерфейсы в Domain)

### Separation of Concerns
- Каждый слой имеет четко определенную ответственность
- Бизнес-логика изолирована в Domain слое
- Технические детали вынесены в Infrastructure

### Testability
- Легкое тестирование за счет dependency injection
- Возможность мокирования внешних зависимостей
- Чистые доменные объекты без внешних зависимостей

## 📁 Структура проекта

```
payment-system/
├── src/
│   ├── domain/                    # Доменный слой
│   │   ├── __init__.py
│   │   ├── entities.py           # Order, OrderLine
│   │   ├── value_objects.py      # Money
│   │   ├── exceptions.py         # Доменные исключения
│   │   └── interfaces.py         # OrderRepository, PaymentGateway
│   │
│   ├── application/              # Слой приложения
│   │   ├── __init__.py
│   │   ├── use_cases.py         # PayOrderUseCaseImpl
│   │   ├── dto.py               # PayOrderRequest, PayOrderResponse
│   │   └── interfaces.py        # PayOrderUseCase
│   │
│   └── infrastructure/           # Инфраструктурный слой
│       ├── __init__.py
│       ├── repositories/
│       │   ├── __init__.py
│       │   └── in_memory_order_repository.py
│       └── payment_gateways/
│           ├── __init__.py
│           └── fake_payment_gateway.py
│
├── tests/                        # Тесты
│   ├── __init__.py
│   ├── test_order_entity.py     # Тесты доменных сущностей
│   └── test_pay_order_use_case.py  # Тесты use cases
│
├── example.py                   # Пример использования
├── requirements.txt             # Зависимости Python
├── README.md                   # Документация
└── .gitignore                  # Игнорируемые файлы Git
```

## 🛠️ Технологии и зависимости

- **Python 3.8+** - основной язык программирования
- **pytest** - фреймворк для тестирования
- **pytest-cov** - инструмент для измерения покрытия кода
- **dataclasses** - для создания неизменяемых структур данных
- **Decimal** - для точных денежных расчетов

## 📚 Ключевые паттерны DDD-lite

1. **Агрегат (Aggregate)** - `Order` как корневая сущность, `OrderLine` как часть агрегата
2. **Value Object** - `Money` как неизменяемый объект-значение
3. **Репозиторий (Repository)** - абстракция для доступа к данным
4. **Use Case** - `PayOrderUseCase` как координатор бизнес-сценария
5. **DTO (Data Transfer Object)** - для передачи данных между слоями

## 🔄 Поток данных

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Контроллер│    │  Use Case    │    │   Domain     │    │Infrastructure│
│   (внешний) │───▶│(Application) │───▶│   Entities   │───▶│  Repository  │
└─────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       │                   │                    │                   │
       │                   │                    │                   │
       │              DTO Request          Бизнес-правила      Сохранение
       │              DTO Response                              в памяти
       │
┌─────────────┐
│   Результат │
│   оплаты    │
└─────────────┘
```

## 🎯 Цели лабораторной работы

1. Практическое применение слоистой архитектуры
2. Реализация принципа инверсии зависимостей (DIP)
3. Создание доменной модели с инвариантами
4. Разделение ответственности между слоями
5. Написание тестов, независимых от инфраструктуры

## 📝 Заметки по расширению

Для промышленного использования систему можно расширить:

1. **База данных** - добавить `PostgreSQLOrderRepository`
2. **Реальный платежный шлюз** - добавить `StripePaymentGateway`
3. **События домена** - реализовать Domain Events для уведомлений
4. **Валидация** - добавить более сложные бизнес-правила
5. **Логирование** - добавить structured logging

## 👥 Автор

Проект выполнен в рамках лабораторной работы по курсу "Архитектура ПО".

## 📄 Лицензия

Учебный проект - свободное использование с указанием авторства.
```

Это полный текст `README.md`, который включает все аспекты проекта:
- Описание архитектуры
- Инструкции по установке и запуску
- Примеры использования
- Описание тестирования
- Структуру проекта
- Принципы проектирования
- И многое другое