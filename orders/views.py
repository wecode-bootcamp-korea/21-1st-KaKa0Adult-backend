import json
from distutils.util import strtobool
from json.decoder   import JSONDecodeError

from django.views           import View
from django.http            import JsonResponse
from django.core.exceptions import MultipleObjectsReturned

from .models         import Order, OrderStatus, OrderItem
from products.models import Product
from users.utils     import login_decorator

class BasketView(View):
    @login_decorator
    def post(self, request):
        try:
            data = json.loads(request.body)

            product       = data['product_id']            
            product_count = data['count']

            if not Product.objects.filter(id=product).exists():
                return JsonResponse({'message':'PRODUCT_DOES_NOT_EXIST'}, status=400)
            
            order, created = Order.objects.get_or_create(
                user         = request.user,
                order_status_id = OrderStatus.BASKET
            )

            if OrderItem.objects.filter(product_id=product, order=order).exists():
                return JsonResponse({'message':'EXIST_ITEM'}, status=400)    

            OrderItem.objects.create(product_id=product, order=order, count=product_count)

            return JsonResponse({'message':'SUCCESS'}, status=201)

        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
        
        except MultipleObjectsReturned:
            return JsonResponse({'message':'MULTIPLE_OBJECT_RETURNED'}, status=400)

        except JSONDecodeError:
            return JsonResponse({'message':'DECODE_ERROR'}, status=400)

    @login_decorator
    def delete(self, request, order_item):
        if not OrderItem.objects.filter(id=order_item).exists():
            return JsonResponse({'message':'INVALID_ORDER_ITEMS'}, status=400)
            
        order_item = OrderItem.objects.get(id=order_item)

        if order_item.order.user != request.user:
            return JsonResponse({'message':'INVALID_USER'}, status=401)

        if order_item.order.order_status.id != OrderStatus.BASKET:
            return JsonResponse({'message':'ORDER_DOSE_NOT_EXIST'}, status=400)

        order_item.delete()

        return JsonResponse({'message':'SUCCESS'}, status=204)

    @login_decorator
    def get(self, request):
        order_items = [{
                'order_item_id': order_item.id,
                'name'         : order_item.product.name,
                'count'        : order_item.count,
                'price'        : order_item.product.price,
                'stock'        : order_item.product.stock,
                'image_url'    : order_item.product.imageurl_set.order_by('id')[0].url,
                'selected'     : order_item.selected
            }for order_item in OrderItem.objects.filter(
                order__user=request.user, 
                order__order_status_id=OrderStatus.BASKET
            )]

        return JsonResponse({'message':'SUCCESS', 'items_in_cart':order_items}, status=200)

    @login_decorator
    def patch(self, request):
        try:
            data          = json.loads(request.body)
            order_item_id = data['order_item_id']
            count         = data['count']
            select        = data['select']
    
            if (type(count) != int or count < 0) and count != None:
                return JsonResponse({'message':'INVALID_COUNT_TYPE'}, status=400)
            
            if not OrderItem.objects.filter(order__user=request.user, id=order_item_id).exists():
                return JsonResponse({'message':'INVALID_ORDER_ITEM'}, status=400)
            
            order_item = OrderItem.objects.filter(id=order_item_id)
            
            if count != None:
                order_item.update(count=count)

            if select != None:
                order_item.update(selected=select)

            return JsonResponse({'message':'SUCCESS'}, status=200)
            
        except KeyError:
            return JsonResponse({'message':'KEY_ERROR'}, status=400)
