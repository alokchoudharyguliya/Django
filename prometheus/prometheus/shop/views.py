# shop/views.py
from django.http import JsonResponse
from .metrics import purchases_counter

def purchase(request):
    item = request.GET.get('item', 'unknown')
    # Increment the custom counter (labelled by item)
    purchases_counter.labels(item=item).inc()
    return JsonResponse({'status': 'success', 'item': item})