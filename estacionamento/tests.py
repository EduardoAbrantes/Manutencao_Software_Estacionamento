from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from . import services
from .models import Cliente, Movimentacao, Vaga, Veiculo


class RegrasEstacionamentoTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome="Maria", cpf="111.111.111-11")
        self.carro = Veiculo.objects.create(
            cliente=self.cliente, placa="ABC1D23", modelo="Gol", tipo="carro"
        )
        self.carro2 = Veiculo.objects.create(
            cliente=self.cliente, placa="XYZ9K88", modelo="Uno", tipo="carro"
        )
        self.moto = Veiculo.objects.create(
            cliente=self.cliente, placa="MOT0R11", modelo="CG", tipo="moto"
        )
        self.v1 = Vaga.objects.create(numero="A1", tipo="carro")
        self.v2 = Vaga.objects.create(numero="A2", tipo="carro")

    def test_entrada_ocupa_vaga_e_saida_libera(self):
        mov = services.registrar_entrada(self.carro, self.v1)
        self.assertTrue(self.v1.ocupada)
        self.assertNotIn(self.v1, Vaga.objects.livres())
        services.registrar_saida(mov)
        self.assertFalse(self.v1.ocupada)
        self.assertIn(self.v1, Vaga.objects.livres())

    def test_vaga_ocupada_nao_aceita_outro_veiculo(self):
        services.registrar_entrada(self.carro, self.v1)
        with self.assertRaises(ValidationError):
            services.registrar_entrada(self.carro2, self.v1)

    def test_veiculo_nao_pode_entrar_duas_vezes(self):
        services.registrar_entrada(self.carro, self.v1)
        with self.assertRaises(ValidationError):
            services.registrar_entrada(self.carro, self.v2)

    def test_tipo_da_vaga_deve_combinar_com_o_veiculo(self):
        with self.assertRaises(ValidationError):
            services.registrar_entrada(self.moto, self.v1)

    def test_vaga_bloqueada_nao_aceita_entrada(self):
        self.v1.ativa = False
        self.v1.save()
        with self.assertRaises(ValidationError):
            services.registrar_entrada(self.carro, self.v1)

    def test_saida_duplicada_e_rejeitada(self):
        mov = services.registrar_entrada(self.carro, self.v1)
        services.registrar_saida(mov)
        with self.assertRaises(ValidationError):
            services.registrar_saida(mov)

    def test_veiculo_pode_voltar_depois_da_saida(self):
        mov = services.registrar_entrada(self.carro, self.v1)
        services.registrar_saida(mov)
        services.registrar_entrada(self.carro, self.v2)
        self.assertEqual(Movimentacao.objects.filter(veiculo=self.carro).count(), 2)


class ViewsTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(nome="Maria", cpf="111.111.111-11")
        self.veiculo = Veiculo.objects.create(
            cliente=self.cliente, placa="ABC1D23", modelo="Gol"
        )
        self.vaga = Vaga.objects.create(numero="A1")

    def test_paginas_abrem(self):
        for nome in ["dashboard", "clientes", "veiculos", "vagas", "movimentacoes",
                     "entrada", "cliente_novo", "veiculo_novo", "vaga_nova"]:
            r = self.client.get(reverse(f"estacionamento:{nome}"))
            self.assertEqual(r.status_code, 200, nome)

    def test_fluxo_entrada_e_saida(self):
        r = self.client.post(
            reverse("estacionamento:entrada"),
            {"veiculo": self.veiculo.pk, "vaga": self.vaga.pk},
        )
        self.assertRedirects(r, reverse("estacionamento:dashboard"))
        mov = Movimentacao.objects.get()
        self.client.post(reverse("estacionamento:saida", args=[mov.pk]))
        mov.refresh_from_db()
        self.assertIsNotNone(mov.saida)

    def test_placa_e_normalizada(self):
        self.client.post(
            reverse("estacionamento:veiculo_novo"),
            {"cliente": self.cliente.pk, "placa": "dEf 4g56", "modelo": "Onix", "tipo": "carro"},
        )
        self.assertTrue(Veiculo.objects.filter(placa="DEF4G56").exists())
