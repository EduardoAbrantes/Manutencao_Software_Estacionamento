from django.contrib import admin

from .models import Cliente, Movimentacao, Vaga, Veiculo


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nome", "cpf", "telefone", "email")
    search_fields = ("nome", "cpf")


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ("placa", "modelo", "tipo", "cliente")
    search_fields = ("placa", "modelo", "cliente__nome")
    list_filter = ("tipo",)


@admin.register(Vaga)
class VagaAdmin(admin.ModelAdmin):
    list_display = ("numero", "tipo", "ativa")
    list_filter = ("tipo", "ativa")


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    list_display = ("veiculo", "vaga", "entrada", "saida")
    list_filter = ("vaga",)
