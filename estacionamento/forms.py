from django import forms

from .models import Cliente, Movimentacao, Vaga, Veiculo


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nome", "cpf", "telefone", "email"]


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ["cliente", "placa", "modelo", "cor", "tipo"]

    def clean_placa(self):
        placa = self.cleaned_data["placa"].upper().replace(" ", "")
        return placa


class VagaForm(forms.ModelForm):
    class Meta:
        model = Vaga
        fields = ["numero", "tipo", "ativa"]


class EntradaForm(forms.Form):
    veiculo = forms.ModelChoiceField(queryset=Veiculo.objects.none())
    vaga = forms.ModelChoiceField(queryset=Vaga.objects.none())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # só veículos que não estão dentro e só vagas livres
        dentro = Movimentacao.objects.filter(saida__isnull=True).values("veiculo_id")
        self.fields["veiculo"].queryset = Veiculo.objects.exclude(
            pk__in=dentro
        ).select_related("cliente")
        self.fields["vaga"].queryset = Vaga.objects.livres()
