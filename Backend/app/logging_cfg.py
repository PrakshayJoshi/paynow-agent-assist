
import logging, json

logging.basicConfig(level=logging.INFO, format="%(message)s")
_logger = logging.getLogger("app")

def log_json(**kwargs):
    try:
        _logger.info(json.dumps(kwargs, ensure_ascii=False))
    except Exception as e:
        _logger.info(json.dumps({"log_error": str(e)}))

def mask_customer(customer_id: str) -> str:
    if not customer_id:
        return ""
    s = str(customer_id)
    tail = s[-3:] if len(s) > 3 else s
    return f"{s[:1]}***{tail}"
