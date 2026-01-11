from dataclasses import dataclass
from decimal import Decimal
from typing import Union
from .exceptions import InvalidMoneyValueException


@dataclass(frozen=True)
class Money:
    """Value Object для представления денег"""
    amount: Decimal
    currency: str = "USD"
    
    def __post_init__(self):
        if self.amount < 0:
            raise InvalidMoneyValueException("Amount cannot be negative")
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add money with different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __mul__(self, multiplier: Union[int, Decimal]) -> 'Money':
        return Money(self.amount * Decimal(multiplier), self.currency)
    
    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"
    
    @classmethod
    def from_float(cls, amount: float, currency: str = "USD") -> 'Money':
        """Создание Money из float"""
        return cls(Decimal(str(amount)), currency)
