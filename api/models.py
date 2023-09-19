from django.db import models
from django.contrib.auth import get_user_model


class Produto(models.Model):
    descricao = models.TextField(null=False)
    valor = models.FloatField(null=False)
    data_validade = models.DateField()
    estoque = models.IntegerField(null=False)
    criado_em = models.DateTimeField(auto_now=True)
    atualizado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.descricao} - {self.valor}"


class Pedido(models.Model):
    class Status(models.TextChoices):
        CANCELADO = "Cancelado"
        ABERTO = "Aberto"
        PROCESSANDO = "Processando"
        ENVIADO = "Enviado"
        ENTREGUE = "Entregue"

    status = models.TextField(choices=Status.choices, default=Status.ABERTO)
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        related_name="pedidos",
    )
    criado_em = models.DateTimeField(auto_now=True)
    atualizado_em = models.DateTimeField(auto_now_add=True)


class CarrinhoCompra(models.Model):
    valor_total = models.FloatField(null=False)
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, null=True, related_name="carrinhos"
    )
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        related_name="carrinhos",
    )
    criado_em = models.DateTimeField(auto_now=True)
    atualizado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.valor_total}"


class CarrinhoCompraItem(models.Model):
    quantidade = models.IntegerField(null=False)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    carrinho = models.ForeignKey(
        CarrinhoCompra, on_delete=models.CASCADE, related_name="itens"
    )
    valor_produto = models.FloatField(null=False)
    valor_total = models.FloatField(null=False)
    criado_em = models.DateTimeField(auto_now=True)
    atualizado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.quantidade}x - {self.produto.descricao} - {self.valor_total}"


class AvaliacaoProduto(models.Model):
    nota = models.FloatField(null=False)
    conteudo = models.TextField(null=False)
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=False,
        related_name="avaliacoes",
    )
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, null=False, related_name="avaliacoes"
    )
    criado_em = models.DateTimeField(auto_now=True)
    atualizado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.nota} - {self.conteudo}"


class ComentarioProduto(models.Model):
    mensagem: models.TextField(null=False)
    usuario = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=False,
        related_name="comentarios",
    )
    produto = models.ForeignKey(
        Produto, on_delete=models.CASCADE, null=False, related_name="comentarios"
    )
    criado_em = models.DateTimeField(auto_now=True)
    atualizado_em = models.DateTimeField(auto_now_add=True)
