import os
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception, before_sleep_log
from google import genai
from google.genai import types
from google.genai import errors
from google.genai.errors import ClientError

from ai.base import BaseAIModel, ModelResult

# Configure basic logging if it hasn't been set up yet in the app
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def _is_retryable_error(e: Exception) -> bool:
    """Return True if the error is a transient network or 503 error."""
    if getattr(e, 'code', None) == 503:
        return True
    if isinstance(e, (TimeoutError, OSError)):
        return True
    return False

class GeminiModel(BaseAIModel):
    DEFAULT_MODEL = 'gemini-3-flash-preview'
    DEFAULT_BACKUP = 'gemini-2.5-flash'
    DEFAULT_TIMEOUT = 480000

    PRICING = {
        'gemini-3-flash-preview': {'input': 0.50, 'output': 3.00},
        'gemini-2.5-flash': {'input': 0.30, 'output': 2.50},
        'gemini-2.5-pro': {'input': 1.25, 'output': 10.00},
    }

    def __init__(self, client: genai.Client | None = None, api_key: str | None = None, model_name: str | None = None, backup_model: str | None = None):
        if client:
            self._client = client
        else:
            api_key = api_key or os.getenv('GEMINIAPIKEY')
            self._client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=self.DEFAULT_TIMEOUT))
        self._model_name = model_name or self.DEFAULT_MODEL
        self._backup_model = backup_model or self.DEFAULT_BACKUP

    @property
    def name(self) -> str:
        return self._model_name

    def generate(self, prompt: str, system_instruction: str = "", temperature: float = 0.1, response_mime_type: str = "text/plain", response_schema: dict | None = None) -> ModelResult:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=temperature,
            response_mime_type=response_mime_type
        )
        if response_schema:
            config.response_schema = response_schema
            
        config = self._ensure_timeout_config(config)
        return self._generate_with_retry(config, prompt)

    def _ensure_timeout_config(self, config: types.GenerateContentConfig) -> types.GenerateContentConfig:
        current_options = getattr(config, 'http_options', None)
        if current_options and getattr(current_options, 'timeout', None) is not None:
            return config

        config.http_options = types.HttpOptions(timeout=self.DEFAULT_TIMEOUT)
        return config

    def _calculate_cost(self, response, model_name: str) -> tuple:
        if not hasattr(response, 'usage_metadata'):
            return 0, 0, 0.0

        rates = self.PRICING.get(model_name, self.PRICING['gemini-2.5-flash'])
        usage = response.usage_metadata
        input_tokens = usage.prompt_token_count
        output_tokens = usage.candidates_token_count

        input_cost = (input_tokens / 1_000_000) * rates['input']
        output_cost = (output_tokens / 1_000_000) * rates['output']
        total_cost = input_cost + output_cost

        logger.info(f"--- Cost Report ({model_name}) ---")
        logger.info(f"Input:  {input_tokens:,} tokens (${input_cost:.4f})")
        logger.info(f"Output: {output_tokens:,} tokens (${output_cost:.4f})")
        logger.info(f"Total:  ${total_cost:.4f}")

        return input_tokens, output_tokens, total_cost

    def _extract_retry_delay(self, error) -> float | None:
        if hasattr(error, 'details') and error.details:
            for detail in error.details:
                if hasattr(detail, 'retry_delay') and detail.retry_delay:
                    return float(detail.retry_delay.rstrip('s'))
        return None

    def _generate_with_retry(self, config: types.GenerateContentConfig, contents: str) -> ModelResult:
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=2, min=2, max=10),
            retry=retry_if_exception(_is_retryable_error),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=True
        )
        def attempt_generation(model_name_to_use):
            logger.info(f"Attempting to generate content with model '{model_name_to_use}'...")
            response = self._client.models.generate_content(
                model=model_name_to_use,
                config=config,
                contents=contents
            )
            if response is None or not hasattr(response, 'text') or response.text is None:
                raise OSError("Empty/None response received")
            return response

        current_model = self._model_name
        fallback_used = False

        try:
            response = attempt_generation(current_model)
            
        except Exception as e:
            # Check if it's a Quota issue (429)
            if getattr(e, 'code', None) == 429:
                retry_delay = self._extract_retry_delay(e)
                if retry_delay:
                    logger.warning(f"--- Quota exceeded (429). Retry after {retry_delay}s ---")
                    time.sleep(retry_delay)
            elif isinstance(e, ClientError):
                logger.warning(f"--- Rate limit detected ({type(e).__name__}). ---")
            else:
                logger.warning(f"Primary model '{current_model}' failed: {e}")

            logger.warning(f"--- Switching to backup model: '{self._backup_model}' ---")
            current_model = self._backup_model
            fallback_used = True

            try:
                response = attempt_generation(current_model)
            except Exception as fallback_error:
                logger.error(f"Backup model also failed: {fallback_error}")
                return ModelResult(model_name=current_model, content="", success=False, error=str(fallback_error))

        input_tokens, output_tokens, cost = self._calculate_cost(response, current_model)
        return ModelResult(
            model_name=current_model,
            content=response.text,
            success=True,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            fallback_used=fallback_used
        )
