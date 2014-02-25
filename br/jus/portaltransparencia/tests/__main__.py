#!/usr/bin/env python
# -*- coding: utf-8 -*-
from br.jus.portaltransparencia import despesas
from br.jus.portaltransparencia import enums
from datetime import date, timedelta
from decimal import Decimal

import os
import unittest


class TestaDespesasUtil(unittest.TestCase):

    def setUp(self):
        self.inicio = date(day=1, month=7, year=2013)
        self.fim = date(day=31, month=7, year=2013)
        self.response = open(
            os.path.join(os.path.dirname(__file__), 'test_fixture.xml')
        )
        self.response_vazio = open(
            os.path.join(os.path.dirname(__file__), 'test_fixture_vazio.xml')
        )

    def tearDown(self):
        self.response.close()

    def testa_prepara_url_para_consulta(self):
        url = despesas.prepara_url(
            inicio=self.inicio,
            fim=self.fim,
            elemento = enums.elemento.DIARIAS_CIVIL.value,
            orgaoSuperior = enums.orgaoSuperior.JT.value,
            unidade = enums.unidade.TRT13.value
        )

        self.assertIn(
            "http://www.portaltransparencia.jus.br/despesas/rLista.php?" +
            "periodoInicio=01%2F07%2F2013&periodoFim=31%2F07%2F2013" +
            "&faseDespesa=ob&orgaoSuperior=15000&unidadeOrcamentaria=15114" +
            "&unidadeGestora=&elementoDespesa=14&nd=",
            url,
            ""
        )

    def testa_ordem_dos_campos_do_resultado(self):
        esperado = despesas.Despesa(
            data=date(2013, 7, 1),
            documento='2013OB802053',
            origem='2013NE000065',
            especie=None,
            orgaoSuperior='JUSTICA DO TRABALHO',
            unidade='TRIBUNAL REGIONAL DO TRABALHO DA 13A. REGIAO',
            favorecido='ANA PAULA AZEVEDO SA CAMPOS PORTO',
            gestora='TRIBUNAL REGIONAL DO TRABALHO DA 13A.REGIAO',
            fase='Pagamento',
            valor=Decimal('3946.38'),
            elemento='DIARIAS - PESSOAL CIVIL',
            tipoDocumento=u'Ordem Banc\xe1ria (OB)',
            codGestao='00001',
            codGestora='080005',
            evento='531335',
        )

        resultados = despesas.lista_resultados(
            self.response
        )

        self.assertEqual(
            resultados[0],
            esperado
        )

    def testa_lista_resultados(self):
        resultados = despesas.lista_resultados(
            self.response
        )
        self.assertEquals(len(list(resultados)), 89)

    def testa_lista_resultados_vazia(self):
        resultados = despesas.lista_resultados(self.response_vazio)
        self.assertEquals(len(list(resultados)), 0)

    def testa_totaliza_valor(self):
        soma = despesas.totaliza_valor(
            despesas.lista_resultados(self.response)
        )
        self.assertEquals(soma, Decimal("73718.72"))


class TestaConsultas(unittest.TestCase):

    def setUp(self):
        self.inicio = date(2013, 8, 1)
        self.fim = date(2013, 8, 31)

    def test_pega_diarias(self):
        resultados = despesas.consulta(
            inicio=self.inicio,
            fim=self.fim,
            orgaoSuperior = enums.orgaoSuperior.JT.value,
            unidade = enums.unidade.TRT13.value,
            elemento = enums.elemento.DIARIAS_CIVIL.value,
        )

        # confirma o total de resultados
        total = 153
        self.assertEquals(len(resultados), total)

        diarias_filtradas = filter(
            lambda x: x.elemento == enums.elemento.DIARIAS_CIVIL.label,
            resultados
        )

        #todas as entradas sao diarias
        self.assertEquals(len(diarias_filtradas), total)

        pagamentos_filtrados = filter(
            lambda x: x.fase == enums.fase.PAGAMENTO.label,
            resultados
        )

        #todas as entradas sao pagamentos
        self.assertEquals(len(pagamentos_filtrados), total)

    def testa_consulta_invalida(self):

        resultados = despesas.consulta(
            # inicio e fim como datas futuras
            inicio=date.today() + timedelta(days=1),
            fim=date.today() + timedelta(days=2),
            orgaoSuperior=enums.orgaoSuperior.JT.value,
            fase=enums.fase.PAGAMENTO.value,
        )

        self.assertTrue(isinstance(resultados, list))
        self.assertEqual(len(resultados), 0)


if __name__ == '__main__':
    unittest.main()