"""Regras de negócio do estacionamento (entrada/saída e controle de vagas)."""
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import Movimentacao, Vaga


def registrar_entrada(veiculo, vaga):
    try:
        with transaction.atomic():
            vaga = Vaga.objects.select_for_update().get(pk=vaga.pk)

            if not vaga.ativa:
                raise ValidationError("Esta vaga está bloqueada.")
            if vaga.tipo != veiculo.tipo:
                raise ValidationError(
                    f"A vaga {vaga.numero} é de {vaga.get_tipo_display().lower()} "
                    f"e o veículo é {veiculo.get_tipo_display().lower()}."
                )
            if vaga.ocupada:
                raise ValidationError(f"A vaga {vaga.numero} já está ocupada.")
            if veiculo.dentro:
                raise ValidationError(
                    f"O veículo {veiculo.placa} já está no estacionamento."
                )

            return Movimentacao.objects.create(veiculo=veiculo, vaga=vaga)
    except IntegrityError:
        # corrida entre duas requisições: as constraints do banco seguram
        raise ValidationError("Vaga ou veículo já registrado. Tente novamente.")


def registrar_saida(movimentacao):
    with transaction.atomic():
        mov = Movimentacao.objects.select_for_update().get(pk=movimentacao.pk)
        if mov.saida is not None:
            raise ValidationError("Esta saída já foi registrada.")
        mov.saida = timezone.now()
        mov.save(update_fields=["saida"])
        return mov
