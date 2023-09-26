from django.urls import path, include
from rest_framework import routers

from api import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"produtos", views.ProdutoViewSet)
router.register(r"carrinho/adicionar", views.CarrinhoCompraAdicionarViewSet)
router.register(r"carrinho/atualizar", views.CarrinhoCompraAtualizarViewSet)
router.register(r"carrinho/remover", views.CarrinhoCompraDeletarViewSet)
router.register(r"carrinho", views.CarrinhoCompraAtualViewSet)
router.register(r"pedidos/criar", views.CriarPedidoViewSet)
router.register(r"pedidos/atualizar", views.AtualizarPedidoViewSet)
router.register(r"pedidos/cancelar", views.CancelarPedidoViewSet)
router.register(r"pedidos", views.PedidoViewSet)
router.register(r"usuarios", views.UsuarioViewSet)
router.register(r"consultas", views.ConsultasViewSet, basename='consultas')

urlpatterns = [
    path("", include(router.urls)),
]
