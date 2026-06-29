from decimal import Decimal

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cart.models import Cart
from .models import Order
from .serializers import OrderSerializer


class OrderListCreateView(generics.ListCreateAPIView):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):

        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response(
                {"message": "Cart is empty"},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_orders = []

        for item in cart_items:

            order = Order.objects.create(
                user=request.user,
                product=item.product,
                quantity=item.quantity,
                total_price=Decimal(item.product.price) * item.quantity
            )

            created_orders.append(order)

        cart_items.delete()

        serializer = OrderSerializer(created_orders, many=True)

        return Response(serializer.data)