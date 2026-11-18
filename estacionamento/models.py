from django.db import models
from django.db.models import Q
from django.utils import timezone


class TipoVeiculo(models.TextChoices):
    CARRO = "carro", "Carro"
    MOTO = "moto", "Moto"


class Cliente(models.Model):
    nome = models.CharField(max_length=120)
    cpf = models.CharField("CPF", max_length=14, unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.cpf})"


class Veiculo(models.Model):
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name="veiculos"
    )
    placa = models.CharField(max_length=8, unique=True)
    modelo = models.CharField(max_length=60)
    cor = models.CharField(max_length=30, blank=True)
    tipo = models.CharField(
        max_length=10, choices=TipoVeiculo.choices, default=TipoVeiculo.CARRO
    )

    class Meta:
        ordering = ["placa"]
        verbose_name = "veículo"
        verbose_name_plural = "veículos"

    def __str__(self):
        return f"{self.placa} - {self.modelo}"

    @property
    def dentro(self):
        return self.movimentacoes.filter(saida__isnull=True).exists()


class VagaQuerySet(models.QuerySet):
    def livres(self):
        ocupadas = Movimentacao.objects.filter(saida__isnull=True).values("vaga_id")
        return self.filter(ativa=True).exclude(pk__in=ocupadas)

    def ocupadas(self):
        ocupadas = Movimentacao.objects.filter(saida__isnull=True).values("vaga_id")
        return self.filter(pk__in=ocupadas)


class Vaga(models.Model):
    numero = models.CharField("número", max_length=10, unique=True)
    tipo = models.CharField(
        max_length=10, choices=TipoVeiculo.choices, default=TipoVeiculo.CARRO
    )
    ativa = models.BooleanField(
        default=True, help_text="Desmarque para bloquear a vaga (manutenção, reserva...)."
    )

    objects = VagaQuerySet.as_manager()

    class Meta:
        ordering = ["numero"]

    def __str__(self):
        return f"Vaga {self.numero} ({self.get_tipo_display()})"

    @property
    def ocupada(self):
        return self.movimentacoes.filter(saida__isnull=True).exists()

    @property
    def movimentacao_atual(self):
        return self.movimentacoes.filter(saida__isnull=True).select_related("veiculo").first()


class Movimentacao(models.Model):
    veiculo = models.ForeignKey(
        Veiculo, on_delete=models.PROTECT, related_name="movimentacoes"
    )
    vaga = models.ForeignKey(
        Vaga, on_delete=models.PROTECT, related_name="movimentacoes"
    )
    entrada = models.DateTimeField(default=timezone.now)
    saida = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-entrada"]
        verbose_name = "movimentação"
        verbose_name_plural = "movimentações"
        constraints = [
            # um veículo só pode estar em um lugar por vez
            models.UniqueConstraint(
                fields=["veiculo"],
                condition=Q(saida__isnull=True),
                name="uniq_veiculo_dentro",
            ),
            # uma vaga só pode ter um veículo por vez
            models.UniqueConstraint(
                fields=["vaga"],
                condition=Q(saida__isnull=True),
                name="uniq_vaga_ocupada",
            ),
        ]

    def __str__(self):
        return f"{self.veiculo.placa} em {self.vaga.numero}"

    @property
    def aberta(self):
        return self.saida is None

    @property
    def permanencia(self):
        fim = self.saida or timezone.now()
        return fim - self.entrada
