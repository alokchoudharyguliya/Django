# api/metrics.py
from prometheus_client import Counter

item_created_counter = Counter(
    'api_items_created_total',
    'Total number of items created via API'
)