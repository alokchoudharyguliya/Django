# shop/metrics.py
from prometheus_client import Counter

# This counter will count the number of purchases
purchases_counter = Counter(
    'shop_purchases_total',         # name (Prometheus convention)
    'Total number of purchases',    # description
    ['item']                        # label: to record what item was purchased
)