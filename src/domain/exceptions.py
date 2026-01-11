class DomainException(Exception):
    """Базовое исключение доменного слоя"""
    pass


class EmptyOrderException(DomainException):
    """Исключение для пустого заказа"""
    pass


class OrderAlreadyPaidException(DomainException):
    """Исключение для уже оплаченного заказа"""
    pass


class OrderModificationException(DomainException):
    """Исключение при попытке изменить оплаченный заказ"""
    pass


class InvalidMoneyValueException(DomainException):
    """Исключение для невалидной суммы денег"""
    pass
