# backend/app/core/exceptions.py
from __future__ import annotations


class QuantAIException(Exception):
    pass


class AuthorizationError(QuantAIException):
    pass


class BrokerError(QuantAIException):
    pass


class StrategyBlockedError(QuantAIException):
    pass
