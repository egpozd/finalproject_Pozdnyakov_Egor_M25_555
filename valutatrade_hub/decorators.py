import functools
from datetime import datetime
from valutatrade_hub.logging_config import logger


def log_action(action: str, verbose: bool = False):
    """
    Декоратор для логирования действий пользователя
    
    Args:
        action: Название действия (BUY, SELL, REGISTER, LOGIN)
        verbose: Подробное логирование (состояние до/после)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Извлекаем информацию о пользователе и параметрах
            user_info = "unknown"
            currency_code = kwargs.get('currency_code', '')
            amount = kwargs.get('amount', 0.0)
            rate = kwargs.get('rate', 0.0)
            base = kwargs.get('base', 'USD')
            
            # Пытаемся получить информацию о пользователе из аргументов
            for arg in args:
                if hasattr(arg, 'username'):
                    user_info = arg.username
                elif hasattr(arg, 'user_id'):
                    user_info = f"user_id:{arg.user_id}"
            
            start_time = datetime.now()
            result = "OK"
            
            try:
                # Выполняем функцию
                return_value = func(*args, **kwargs)
                
                # Логируем успешное выполнение
                log_data = {
                    'action': action,
                    'user': user_info,
                    'currency_code': currency_code,
                    'amount': amount,
                    'rate': rate,
                    'base': base,
                    'result': result,
                    'duration_ms': (datetime.now() - start_time).total_seconds() * 1000
                }
                
                if verbose and hasattr(return_value, '__dict__'):
                    log_data['details'] = str(return_value)
                
                logger.info(f"{action} operation completed", extra=log_data)
                return return_value
                
            except Exception as e:
                result = "ERROR"
                
                # Логируем ошибку
                log_data = {
                    'action': action,
                    'user': user_info,
                    'currency_code': currency_code,
                    'amount': amount,
                    'result': result,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'duration_ms': (datetime.now() - start_time).total_seconds() * 1000
                }
                
                logger.error(f"{action} operation failed", extra=log_data)
                raise
        
        return wrapper
    return decorator