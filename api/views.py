from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action
from django.contrib.auth.models import User
from django.db.models import Q
from api.helpers import create_url_path
import requests

from api.models import (
    AvaliacaoProduto,
    Pedido,
    Produto,
    CarrinhoCompra,
)
from api.serializers import (
    CancelarPedidoSerializer,
    CarrinhoComprasAtualSerializer,
    ComentarioProdutoSerializer,
    CriarPedidoSerializer,
    AtualizarPedidoSerializer,
    CriarUsuarioSerializer,
    PedidoDetalhadoSerializer,
    PedidoSerializer,
    ProdutoDetalhadoSerializer,
    ProdutoSerializer,
    CarrinhoComprasSerializer,
    CarrinhoComprasSerializer,
    UsuarioSerializer,
    AvaliacaoProdutoSerializer,
)


class ProdutoViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProdutoDetalhadoSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=["GET"])
    def avaliacoes(self, request, pk=None):
        produto = self.get_object()
        avaliacoes = AvaliacaoProduto.objects.filter(produto=produto)
        serializer = AvaliacaoProdutoSerializer(avaliacoes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["POST"])
    def avaliacao(self, request, pk=None):
        request.data["produto"] = self.get_object().pk
        request.data["usuario"] = request.user.pk
        serializer = AvaliacaoProdutoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)

    @action(detail=True, methods=["POST"])
    def comentario(self, request, pk=None):
        request.data["produto"] = self.get_object().pk
        request.data["usuario"] = request.user.pk
        serializer = ComentarioProdutoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=201)


class CarrinhoCompraAtualViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CarrinhoCompra.objects.all()
    serializer_class = CarrinhoComprasAtualSerializer

    def get_queryset(self):
        return CarrinhoCompra.objects.filter(
            Q(usuario=self.request.user) and Q(pedido=None)
        )


class CarrinhoCompraAdicionarViewSet(viewsets.ViewSet):
    queryset = CarrinhoCompra.objects.all()
    serializer_class = CarrinhoComprasSerializer

    def create(self, request):
        request.data["usuario"] = request.user.pk
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)


class CarrinhoCompraAtualizarViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = CarrinhoCompra.objects.all()
    serializer_class = CarrinhoComprasSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            self.get_object(), data=request.data, partial=False
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=200)


class CarrinhoCompraDeletarViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = CarrinhoCompra.objects.all()
    serializer_class = CarrinhoComprasSerializer


class PedidoViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = Pedido.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PedidoDetalhadoSerializer
        return PedidoSerializer


class CriarPedidoViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Pedido.objects.all()
    serializer_class = CriarPedidoSerializer


class AtualizarPedidoViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Pedido.objects.all()
    serializer_class = AtualizarPedidoSerializer


class CancelarPedidoViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Pedido.objects.all()
    serializer_class = CancelarPedidoSerializer

    def destroy(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            self.get_object(), data=request.data, partial=False
        )
        serializer.is_valid(raise_exception=True)
        serializer.cancelar()
        return Response(serializer.data, status=200)


class UsuarioViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return []
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return CriarUsuarioSerializer
        return UsuarioSerializer


class AvaliacaoProdutoViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AvaliacaoProdutoSerializer
    queryset = AvaliacaoProduto.objects.all()

    def get_queryset(self):
        return AvaliacaoProduto.objects.filter(produto_id=self.kwargs["id"])

    def list(self, request, *args, **kwargs):
        return AvaliacaoProduto.objects.filter(produto_id=self.kwargs["id"])

class ConsultasViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['GET'], url_path=create_url_path('cep/:cep'))
    def cep(self, request, cep: str):
        
        url = f'https://viacep.com.br/ws/{cep}/json/'

        # Fazer a requisição GET para a URL e verificar se o status code é 200
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            cep = data['cep']
            rua = data['logradouro']
            bairro = data['bairro']
            cidade = data['localidade']
            estado = data['uf']

            result = {
            'cep': cep,
            'rua': rua,
            'bairro': bairro,
            'cidade': cidade,
            'estado': estado
            }
            
            return Response(result)
        else:
        # Retornar uma resposta de erro se o status code não for 200
            return Response({'error': 'CEP inválido ou não encontrado'}, status=response.status_code)