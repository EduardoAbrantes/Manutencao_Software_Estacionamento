from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, FormView, ListView, TemplateView, UpdateView

from . import services
from .forms import ClienteForm, EntradaForm, VagaForm, VeiculoForm
from .models import Cliente, Movimentacao, Vaga, Veiculo


class DashboardView(TemplateView):
    template_name = "estacionamento/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        vagas = list(Vaga.objects.all())
        abertas = {
            m.vaga_id: m
            for m in Movimentacao.objects.filter(saida__isnull=True).select_related(
                "veiculo"
            )
        }
        for v in vagas:
            v.mov_atual = abertas.get(v.pk)
            v.livre = v.ativa and v.mov_atual is None
        ctx["vagas"] = vagas
        ctx["total"] = sum(1 for v in vagas if v.ativa)
        ctx["ocupadas"] = len(abertas)
        ctx["livres"] = sum(1 for v in vagas if v.livre)
        return ctx


# ---- CRUD simples ----------------------------------------------------------
class FormMixin_:
    template_name = "estacionamento/form.html"
    titulo = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = self.titulo
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Salvo com sucesso.")
        return super().form_valid(form)


class ClienteList(ListView):
    model = Cliente
    paginate_by = 20


class ClienteCreate(FormMixin_, CreateView):
    model = Cliente
    form_class = ClienteForm
    success_url = reverse_lazy("estacionamento:clientes")
    titulo = "Novo cliente"


class ClienteUpdate(FormMixin_, UpdateView):
    model = Cliente
    form_class = ClienteForm
    success_url = reverse_lazy("estacionamento:clientes")
    titulo = "Editar cliente"


class VeiculoList(ListView):
    queryset = Veiculo.objects.select_related("cliente")
    paginate_by = 20


class VeiculoCreate(FormMixin_, CreateView):
    model = Veiculo
    form_class = VeiculoForm
    success_url = reverse_lazy("estacionamento:veiculos")
    titulo = "Novo veículo"


class VeiculoUpdate(FormMixin_, UpdateView):
    model = Veiculo
    form_class = VeiculoForm
    success_url = reverse_lazy("estacionamento:veiculos")
    titulo = "Editar veículo"


class VagaList(ListView):
    model = Vaga


class VagaCreate(FormMixin_, CreateView):
    model = Vaga
    form_class = VagaForm
    success_url = reverse_lazy("estacionamento:vagas")
    titulo = "Nova vaga"


class VagaUpdate(FormMixin_, UpdateView):
    model = Vaga
    form_class = VagaForm
    success_url = reverse_lazy("estacionamento:vagas")
    titulo = "Editar vaga"


# ---- Entrada / saída -------------------------------------------------------
class MovimentacaoList(ListView):
    queryset = Movimentacao.objects.select_related("veiculo", "vaga")
    paginate_by = 30


class EntradaView(FormView):
    template_name = "estacionamento/form.html"
    form_class = EntradaForm
    success_url = reverse_lazy("estacionamento:dashboard")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titulo"] = "Registrar entrada"
        return ctx

    def form_valid(self, form):
        try:
            mov = services.registrar_entrada(
                form.cleaned_data["veiculo"], form.cleaned_data["vaga"]
            )
        except ValidationError as e:
            for msg in e.messages:
                form.add_error(None, msg)
            return self.form_invalid(form)
        messages.success(
            self.request, f"Entrada registrada: {mov.veiculo.placa} na vaga {mov.vaga.numero}."
        )
        return super().form_valid(form)


class SaidaView(View):
    http_method_names = ["post"]

    def post(self, request, pk):
        mov = get_object_or_404(Movimentacao, pk=pk)
        try:
            mov = services.registrar_saida(mov)
        except ValidationError as e:
            messages.error(request, " ".join(e.messages))
        else:
            messages.success(
                request, f"Saída registrada: {mov.veiculo.placa} (vaga {mov.vaga.numero} liberada)."
            )
        return redirect("estacionamento:dashboard")
