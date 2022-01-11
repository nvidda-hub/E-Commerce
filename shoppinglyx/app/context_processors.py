from app.models import Cart

def items_in_cart(request):
    cart_length = 0
    if request.user.is_authenticated:
        cart_length = len(Cart.objects.filter(user=request.user))
    return {
        'cart_length' : cart_length
    }