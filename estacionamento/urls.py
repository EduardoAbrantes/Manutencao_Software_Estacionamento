from django.urls import path

from . import views

app_name = "estacionamento"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("clientes/", views.ClienteList.as_view(), name="clientes"),
    path("clientes/novo/", views.ClienteCreate.as_view(), name="cliente_novo"),
    path("clientes/<int:pk>/editar/", views.ClienteUpdate.as_view(), name="cliente_editar"),
    path("veiculos/", views.VeiculoList.as_view(), name="veiculos"),
    path("veiculos/novo/", views.VeiculoCreate.as_view(), name="veiculo_novo"),
    path("veiculos/<int:pk>/editar/", views.VeiculoUpdate.as_view(), name="veiculo_editar"),
    path("vagas/", views.VagaList.as_view(), name="vagas"),
    path("vagas/nova/", views.VagaCreate.as_view(), name="vaga_nova"),
    path("vagas/<int:pk>/editar/", views.VagaUpdate.as_view(), name="vaga_editar"),
    path("movimentacoes/", views.MovimentacaoList.as_view(), name="movimentacoes"),
    path("entrada/", views.EntradaView.as_view(), name="entrada"),
    path("saida/<int:pk>/", views.SaidaView.as_view(), name="saida"),
]
