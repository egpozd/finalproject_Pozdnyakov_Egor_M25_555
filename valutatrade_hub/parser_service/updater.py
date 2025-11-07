import time
from typing import Dict, Tuple
from valutatrade_hub.parser_service.config import config
from valutatrade_hub.parser_service.api_clients import CoinGeckoClient, ExchangeRateApiClient
from valutatrade_hub.parser_service.storage import storage
from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.logging_config import logger


class RatesUpdater:
    """Класс для координации обновления курсов валют"""
    
    def __init__(self):
        self.coingecko_client = CoinGeckoClient()
        self.exchangerate_client = ExchangeRateApiClient()
        self.storage = storage
    
    def run_update(self, sources: Tuple[str] = ('coingecko', 'exchangerate')) -> Dict:
        """
        Запуск обновления курсов
        
        Args:
            sources: Кортеж источников для обновления
            
        Returns:
            Словарь с результатами обновления
        """
        logger.info("Starting rates update...")
        
        all_rates = {}
        all_sources = {}
        errors = []
        
        start_time = time.time()
        
        # Обновляем курсы из CoinGecko
        if 'coingecko' in sources:
            try:
                logger.info("Fetching rates from CoinGecko...")
                crypto_rates = self.coingecko_client.fetch_rates()
                all_rates.update(crypto_rates)
                
                # Добавляем информацию об источниках
                for pair in crypto_rates.keys():
                    all_sources[pair] = 'CoinGecko'
                
                logger.info(f"CoinGecko: OK ({len(crypto_rates)} rates)")
                
                # Сохраняем исторические данные
                for pair, rate in crypto_rates.items():
                    from_curr, to_curr = pair.split('_')
                    storage.save_historical_rate(
                        from_currency=from_curr,
                        to_currency=to_curr,
                        rate=rate,
                        source='CoinGecko',
                        meta={'request_ms': int((time.time() - start_time) * 1000)}
                    )
                    
            except ApiRequestError as e:
                error_msg = f"CoinGecko: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Обновляем курсы из ExchangeRate-API
        if 'exchangerate' in sources:
            try:
                logger.info("Fetching rates from ExchangeRate-API...")
                fiat_rates = self.exchangerate_client.fetch_rates()
                all_rates.update(fiat_rates)
                
                # Добавляем информацию об источниках
                for pair in fiat_rates.keys():
                    all_sources[pair] = 'ExchangeRate-API'
                
                logger.info(f"ExchangeRate-API: OK ({len(fiat_rates)} rates)")
                
                # Сохраняем исторические данные
                for pair, rate in fiat_rates.items():
                    from_curr, to_curr = pair.split('_')
                    storage.save_historical_rate(
                        from_currency=from_curr,
                        to_currency=to_curr,
                        rate=rate,
                        source='ExchangeRate-API',
                        meta={'request_ms': int((time.time() - start_time) * 1000)}
                    )
                    
            except ApiRequestError as e:
                error_msg = f"ExchangeRate-API: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Сохраняем текущие курсы
        if all_rates:
            saved_count = self.storage.save_current_rates(all_rates, all_sources)
            logger.info(f"Writing {saved_count} rates to {config.RATES_FILE_PATH}")
        else:
            logger.warning("No rates were fetched from any source")
        
        # Формируем результат
        result = {
            'success': len(errors) == 0,
            'rates_count': len(all_rates),
            'errors': errors,
            'duration_ms': int((time.time() - start_time) * 1000)
        }
        
        if result['success']:
            logger.info(f"Update successful. Total rates updated: {result['rates_count']}")
        else:
            logger.warning(f"Update completed with errors. Rates updated: {result['rates_count']}")
        
        return result