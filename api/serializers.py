from rest_framework import serializers

from api.models import (
    ComentarioProduto,
    Pedido,
    Produto,
    CarrinhoCompraItem,
    CarrinhoCompra,
    AvaliacaoProduto,
)
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.db.models import Q


class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = "__all__"


class ComentarioProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComentarioProduto
        fields = "__all__"


class ProdutoDetalhadoSerializer(serializers.ModelSerializer):
    nota_media = serializers.SerializerMethodField(read_only=True)
    comentarios = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Produto
        fields = "__all__"

    def get_nota_media(self, obj):
        avaliacoes = AvaliacaoProduto.objects.filter(produto=obj)
        if len(avaliacoes) < 1:
            media = 0.0
        else:
            media = sum([av.nota for av in avaliacoes]) / len(avaliacoes)
        return "{:.2f}".format(media)

    def get_comentarios(self, obj):
        comentarios = ComentarioProduto.objects.filter(produto=obj)
        return ComentarioProdutoSerializer(comentarios, many=True).data


class CarrinhoComprasItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarrinhoCompraItem
        fields = "__all__"
        extra_kwargs = {
            "carrinho": {"required": False},
            "valor_total": {"required": False},
            "valor_produto": {"required": False},
        }


class CarrinhoComprasAtualSerializer(serializers.ModelSerializer):
    itens = serializers.SerializerMethodField()
    total_dolar = serializers.SerializerMethodField()

    class Meta:
        model = CarrinhoCompra
        fields = "__all__"
        extra_kwargs = {"valor_total": {"required": False}}

    def get_itens(self, obj):
        serializer = CarrinhoComprasItemSerializer(
            CarrinhoCompraItem.objects.filter(carrinho=obj).all(), many=True
        )
        return serializer.data

    def get_total_dolar(self, obj: CarrinhoCompra):
        # TODO: Implementar este método para converter o total em reais em uma api externa e retornar abaixo.
        # Utilizar o campo `obj.valor_total` para enviar para a api.
        # O resultado da api deve ser retornado abaixo.
        return 0.00


class CarrinhoComprasSerializer(serializers.ModelSerializer):
    itens = CarrinhoComprasItemSerializer(many=True)

    class Meta:
        model = CarrinhoCompra
        fields = "__all__"
        extra_kwargs = {"valor_total": {"required": False}}

    def create(self, validated_data):
        itens_data = validated_data.pop("itens")
        carrinho_existente = CarrinhoCompra.objects.filter(
            Q(usuario=validated_data["usuario"]) and Q(pedido=None)
        ).first()
        if carrinho_existente is not None:
            itens_carrinho_existente: list[
                CarrinhoCompraItem
            ] = CarrinhoCompraItem.objects.filter(carrinho=carrinho_existente).all()
            for item in itens_carrinho_existente:
                item.produto.estoque += item.quantidade
                item.produto.save()
            carrinho_existente.delete()
        carrinho = CarrinhoCompra.objects.create(valor_total=0.00, **validated_data)
        itens = []
        valor_total_carrinho = 0.00
        for item_data in itens_data:
            quantidade = item_data["quantidade"]
            produto = item_data["produto"]
            if carrinho_existente is not None:
                produto.refresh_from_db()
            if quantidade > produto.estoque:
                raise serializers.ValidationError(
                    {
                        "itens": [
                            {
                                "produto": int(produto.id),
                                "quantidade": int(quantidade),
                                "detail": f"Produto não possui estoque",
                                "estoque_disponivel": int(produto.estoque),
                            }
                        ]
                    }
                )
            valor_total_item = quantidade * produto.valor
            valor_total_carrinho += valor_total_item
            item = CarrinhoCompraItem.objects.create(
                carrinho=carrinho,
                valor_total=valor_total_item,
                valor_produto=produto.valor,
                **item_data,
            )
            itens.append(item)
            produto.estoque -= quantidade
            produto.save()
        carrinho.valor_total = valor_total_carrinho
        carrinho.save()
        carrinho.itens.set(itens)
        return carrinho

    def update(self, carrinho: CarrinhoCompra, validated_data):
        itens_data = validated_data.pop("itens")
        itens = []
        valor_total_carrinho = 0.00
        instance_itens = CarrinhoCompraItem.objects.filter(carrinho=carrinho).all()
        for item in instance_itens:
            item.produto.estoque += item.quantidade
            item.produto.save()
            item.delete()
        for item_data in itens_data:
            quantidade = item_data["quantidade"]
            produto: Produto = item_data["produto"]
            produto.refresh_from_db()
            if quantidade > produto.estoque:
                raise serializers.ValidationError(
                    {
                        "itens": [
                            {
                                "produto": int(produto.id),
                                "quantidade": int(quantidade),
                                "detail": f"Produto não possui estoque",
                                "estoque_disponivel": int(produto.estoque),
                            }
                        ]
                    }
                )
            valor_total_item = quantidade * produto.valor
            valor_total_carrinho += valor_total_item
            item = CarrinhoCompraItem.objects.create(
                carrinho=carrinho,
                valor_total=valor_total_item,
                valor_produto=produto.valor,
                **item_data,
            )
            itens.append(item)
            produto.estoque -= quantidade
            produto.save()
        carrinho.valor_total = valor_total_carrinho
        carrinho.save()
        carrinho.itens.set(itens)
        return carrinho


class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = "__all__"


class PedidoDetalhadoSerializer(serializers.ModelSerializer):
    carrinhos = serializers.SerializerMethodField()

    class Meta:
        model = Pedido
        fields = "__all__"

    def get_carrinhos(self, obj):
        carrinhos = CarrinhoCompra.objects.filter(pedido__id=obj.id).all()
        carrinhos_serializer = CarrinhoComprasSerializer(carrinhos, many=True)
        return carrinhos_serializer.data


class CriarPedidoSerializer(serializers.ModelSerializer):
    carrinhos = serializers.PrimaryKeyRelatedField(
        queryset=CarrinhoCompra.objects.all(), many=True
    )

    class Meta:
        model = Pedido
        fields = "__all__"


class AtualizarPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ["status"]

    def validate(self, attrs):
        if self.instance.status == Pedido.Status.CANCELADO:
            error_message = "Não é possível cancelar um pedido por este endpoint."
        elif self.instance.status == attrs["status"]:
            error_message = f"Pedido já se encontra {self.instance.status}."
        else:
            error_message = None
        if error_message is not None:
            raise serializers.ValidationError(detail={"detail": error_message})
        return super().validate(attrs)

    def update(self, instance: Pedido, validated_data):
        instance.status = validated_data["status"]
        instance.save()
        return PedidoDetalhadoSerializer(instance).data


class CancelarPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = "__all__"

    def validate(self, attrs):
        if self.instance.status == Pedido.Status.CANCELADO:
            error_message = "Pedido já se encontra cancelado."
        elif self.instance.status == Pedido.Status.ENVIADO:
            error_message = "Pedido não pode ser cancelado, pois já foi enviado."
        elif self.instance.status == Pedido.Status.ENTREGUE:
            error_message = "Pedido não pode ser cancelado, pois já foi entregue."
        else:
            error_message = None
        if error_message is not None:
            raise serializers.ValidationError(detail={"detail": error_message})
        return super().validate(attrs)

    def cancelar(self):
        self.instance.status = Pedido.Status.CANCELADO
        self.instance.save()
        return PedidoDetalhadoSerializer(self.instance).data


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        partial = True
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "date_joined",
        ]


class CriarUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class AvaliacaoProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvaliacaoProduto
        fields = "__all__"

    def validate_nota(self, obj):
        if obj < 0.0:
            raise serializers.ValidationError(
                detail="A nota deve ser maior ou igual a 0.0"
            )
        if obj > 5.0:
            raise serializers.ValidationError(
                detail="A nota deve ser menor ou igual a 5.0"
            )
        return obj
