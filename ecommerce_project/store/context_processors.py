from .models import Cart


def cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            count = sum(item.quantity for item in cart.cartitem_set.all())
        except Cart.DoesNotExist:
            count = 0
    else:
        count = 0
    return {'cart_count': count}
