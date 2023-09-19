from django.contrib import admin

from api.models import Produto, CarrinhoCompra, CarrinhoCompraItem, Pedido

admin.site.register(Produto)
admin.site.register(CarrinhoCompra)
admin.site.register(CarrinhoCompraItem)
admin.site.register(Pedido)
