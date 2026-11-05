// Biblioteca DAX da Single Tecnologia: 60 medidas por área.
// Cada item: area, nome, oque (o que mostra), codigo, dica (opcional).
// Medidas base usadas em todas: ver BASE abaixo. Ao acrescentar medidas, confira a fórmula e mantenha os nomes de tabela.
window.BASE = `Receita = SUM ( Vendas[Valor] )
Custo = SUM ( Vendas[Custo] )
Quantidade = SUM ( Vendas[Quantidade] )
Pedidos = DISTINCTCOUNT ( Vendas[Pedido] )
Orçado = SUM ( Orcamento[Valor] )
Despesas = SUM ( Despesas[Valor] )`;

window.MEDIDAS = [
// ---------- Datas e tempo (12) ----------
{area:"Datas e tempo", nome:"Receita YTD", oque:"Acumulado de janeiro até a data selecionada.", codigo:
`Receita YTD =
TOTALYTD ( [Receita], 'Calendario'[Data] )`},
{area:"Datas e tempo", nome:"Receita MTD", oque:"Acumulado do mês até o dia selecionado.", codigo:
`Receita MTD =
TOTALMTD ( [Receita], 'Calendario'[Data] )`},
{area:"Datas e tempo", nome:"Receita QTD", oque:"Acumulado do trimestre até a data selecionada.", codigo:
`Receita QTD =
TOTALQTD ( [Receita], 'Calendario'[Data] )`},
{area:"Datas e tempo", nome:"Receita AA", oque:"O mesmo período, um ano antes.", codigo:
`Receita AA =
CALCULATE (
    [Receita],
    SAMEPERIODLASTYEAR ( 'Calendario'[Data] )
)`},
{area:"Datas e tempo", nome:"Var % AA", oque:"Quanto cresceu ou caiu contra o ano anterior.", codigo:
`Var % AA =
DIVIDE ( [Receita] - [Receita AA], [Receita AA] )`, dica:"Sem ano anterior, DIVIDE devolve vazio em vez de erro."},
{area:"Datas e tempo", nome:"Receita YTD AA", oque:"O acumulado do ano passado até a mesma data.", codigo:
`Receita YTD AA =
CALCULATE (
    [Receita YTD],
    SAMEPERIODLASTYEAR ( 'Calendario'[Data] )
)`},
{area:"Datas e tempo", nome:"Receita Mês Anterior", oque:"O mês imediatamente antes do selecionado.", codigo:
`Receita Mês Anterior =
CALCULATE (
    [Receita],
    DATEADD ( 'Calendario'[Data], -1, MONTH )
)`, dica:"Troque MONTH por QUARTER para o trimestre anterior."},
{area:"Datas e tempo", nome:"Var % Mês Anterior", oque:"Crescimento contra o mês anterior.", codigo:
`Var % Mês Anterior =
DIVIDE (
    [Receita] - [Receita Mês Anterior],
    [Receita Mês Anterior]
)`},
{area:"Datas e tempo", nome:"Receita 12 Meses", oque:"Soma dos últimos 12 meses até a data selecionada. Tira o efeito da sazonalidade.", codigo:
`Receita 12M =
CALCULATE (
    [Receita],
    DATESINPERIOD (
        'Calendario'[Data],
        MAX ( 'Calendario'[Data] ),
        -12,
        MONTH
    )
)`},
{area:"Datas e tempo", nome:"Média Móvel 3 Meses", oque:"Média mensal dos últimos 3 meses. Suaviza picos e vales.", codigo:
`Média Móvel 3M =
CALCULATE (
    AVERAGEX ( VALUES ( 'Calendario'[AnoMes] ), [Receita] ),
    DATESINPERIOD (
        'Calendario'[Data],
        MAX ( 'Calendario'[Data] ),
        -3,
        MONTH
    )
)`, dica:"Precisa da coluna AnoMes na Calendario (veja \"Antes de começar\")."},
{area:"Datas e tempo", nome:"Receita Acumulada", oque:"Total acumulado desde o início dos dados até a data selecionada.", codigo:
`Receita Acumulada =
CALCULATE (
    [Receita],
    FILTER (
        ALL ( 'Calendario'[Data] ),
        'Calendario'[Data] <= MAX ( 'Calendario'[Data] )
    )
)`},
{area:"Datas e tempo", nome:"Dias com Venda", oque:"Quantos dias do período tiveram pelo menos uma venda.", codigo:
`Dias com Venda =
COUNTROWS (
    FILTER ( VALUES ( 'Calendario'[Data] ), [Receita] > 0 )
)`},

// ---------- Financeiro (12) ----------
{area:"Financeiro", nome:"Margem Bruta", oque:"Quanto sobra da receita depois do custo, em reais.", codigo:
`Margem Bruta =
[Receita] - [Custo]`},
{area:"Financeiro", nome:"Margem Bruta %", oque:"A margem bruta em porcentagem da receita.", codigo:
`Margem Bruta % =
DIVIDE ( [Receita] - [Custo], [Receita] )`},
{area:"Financeiro", nome:"Lucro Líquido", oque:"Receita menos custo e despesas.", codigo:
`Lucro Líquido =
[Receita] - [Custo] - [Despesas]`},
{area:"Financeiro", nome:"Margem Líquida %", oque:"O lucro líquido em porcentagem da receita.", codigo:
`Margem Líquida % =
DIVIDE ( [Lucro Líquido], [Receita] )`},
{area:"Financeiro", nome:"Desvio % do Orçado", oque:"Quanto o realizado ficou acima ou abaixo do orçamento.", codigo:
`Desvio % Orçado =
DIVIDE ( [Receita] - [Orçado], [Orçado] )`, dica:"Orçamento costuma vir por mês: guarde a data no primeiro dia do mês para relacionar com a Calendario."},
{area:"Financeiro", nome:"Atingimento da Meta %", oque:"Quanto da meta já foi alcançado.", codigo:
`Atingimento % =
DIVIDE ( [Receita], [Orçado] )`},
{area:"Financeiro", nome:"Orçado YTD", oque:"O orçamento acumulado no ano.", codigo:
`Orçado YTD =
TOTALYTD ( [Orçado], 'Calendario'[Data] )`},
{area:"Financeiro", nome:"Desvio YTD", oque:"Diferença em reais entre o realizado e o orçado no ano.", codigo:
`Desvio YTD =
[Receita YTD] - [Orçado YTD]`},
{area:"Financeiro", nome:"Ponto de Equilíbrio", oque:"A receita necessária para pagar as despesas do período.", codigo:
`Ponto de Equilíbrio =
DIVIDE ( [Despesas], [Margem Bruta %] )`, dica:"Considera Custo como variável e Despesas como fixas."},
{area:"Financeiro", nome:"Projeção do Mês", oque:"Para onde o mês vai, no ritmo de hoje.", codigo:
`Projeção do Mês =
VAR DiasPassados =
    COUNTROWS (
        FILTER (
            VALUES ( 'Calendario'[Data] ),
            'Calendario'[Data] <= TODAY ()
        )
    )
VAR DiasDoMes = COUNTROWS ( VALUES ( 'Calendario'[Data] ) )
RETURN
    DIVIDE ( [Receita], DiasPassados ) * DiasDoMes`, dica:"Use com um mês selecionado e a Calendario com todos os dias."},
{area:"Financeiro", nome:"Receita Líquida", oque:"Receita depois dos descontos concedidos.", codigo:
`Receita Líquida =
[Receita] - SUM ( Vendas[Desconto] )`},
{area:"Financeiro", nome:"Desconto Médio %", oque:"Quanto de desconto foi dado, em porcentagem da receita.", codigo:
`Desconto Médio % =
DIVIDE ( SUM ( Vendas[Desconto] ), [Receita] )`},

// ---------- Vendas (12) ----------
{area:"Vendas", nome:"Ticket Médio", oque:"Valor médio de cada pedido.", codigo:
`Ticket Médio =
DIVIDE ( [Receita], [Pedidos] )`},
{area:"Vendas", nome:"Itens por Pedido", oque:"Quantas unidades, em média, cada pedido leva.", codigo:
`Itens por Pedido =
DIVIDE ( [Quantidade], [Pedidos] )`},
{area:"Vendas", nome:"Preço Médio", oque:"Receita média por unidade vendida.", codigo:
`Preço Médio =
DIVIDE ( [Receita], [Quantidade] )`},
{area:"Vendas", nome:"Participação %", oque:"O peso de cada categoria no total do que está filtrado.", codigo:
`Participação % =
DIVIDE (
    [Receita],
    CALCULATE (
        [Receita],
        ALLSELECTED ( Produto[Categoria] )
    )
)`, dica:"ALLSELECTED respeita os filtros da página."},
{area:"Vendas", nome:"Participação no Total Geral %", oque:"O peso de cada item no total da empresa, ignorando filtros de produto.", codigo:
`Participação Total % =
DIVIDE (
    [Receita],
    CALCULATE ( [Receita], ALL ( Produto ) )
)`},
{area:"Vendas", nome:"Ranking de Produtos", oque:"A posição de cada produto por receita.", codigo:
`Ranking Produto =
RANKX (
    ALLSELECTED ( Produto[Produto] ),
    [Receita],
    ,
    DESC,
    DENSE
)`},
{area:"Vendas", nome:"Receita dos 10 Maiores Produtos", oque:"Quanto os 10 produtos que mais vendem trazem de receita.", codigo:
`Receita Top 10 =
CALCULATE (
    [Receita],
    TOPN (
        10,
        ALLSELECTED ( Produto[Produto] ),
        [Receita],
        DESC
    )
)`},
{area:"Vendas", nome:"Curva ABC: % Acumulado", oque:"A soma da receita do produto e de todos os que vendem mais que ele, em % do total.", codigo:
`ABC % Acumulado =
VAR ReceitaProduto = [Receita]
VAR Acumulado =
    SUMX (
        FILTER (
            ALLSELECTED ( Produto[Produto] ),
            [Receita] >= ReceitaProduto
        ),
        [Receita]
    )
RETURN
    DIVIDE (
        Acumulado,
        CALCULATE ( [Receita], ALLSELECTED ( Produto[Produto] ) )
    )`, dica:"Use numa tabela com a coluna Produto[Produto]."},
{area:"Vendas", nome:"Curva ABC: Classe", oque:"Classifica o produto em A (80% da receita), B (próximos 15%) ou C.", codigo:
`Classe ABC =
VAR P = [ABC % Acumulado]
RETURN
    SWITCH (
        TRUE (),
        P <= 0.8, "A",
        P <= 0.95, "B",
        "C"
    )`},
{area:"Vendas", nome:"Pedidos AA", oque:"Quantidade de pedidos no mesmo período do ano anterior.", codigo:
`Pedidos AA =
CALCULATE (
    [Pedidos],
    SAMEPERIODLASTYEAR ( 'Calendario'[Data] )
)`},
{area:"Vendas", nome:"Taxa de Conversão %", oque:"Quantas propostas enviadas viraram pedido.", codigo:
`Conversão % =
DIVIDE ( [Pedidos], COUNTROWS ( Propostas ) )`, dica:"Propostas é a tabela de orçamentos comerciais enviados, ligada à Calendario."},
{area:"Vendas", nome:"Status da Meta", oque:"Mostra em texto se o vendedor ou a loja bateu a meta.", codigo:
`Status da Meta =
IF (
    ISBLANK ( [Orçado] ),
    BLANK (),
    IF ( [Receita] >= [Orçado], "Atingiu", "Abaixo da meta" )
)`},

// ---------- Clientes (8) ----------
{area:"Clientes", nome:"Clientes Ativos", oque:"Quantos clientes compraram no período.", codigo:
`Clientes Ativos =
DISTINCTCOUNT ( Vendas[ClienteID] )`},
{area:"Clientes", nome:"Clientes Novos", oque:"Clientes cuja primeira compra aconteceu no período.", codigo:
`Clientes Novos =
VAR Inicio = MIN ( 'Calendario'[Data] )
RETURN
    COUNTROWS (
        FILTER (
            VALUES ( Vendas[ClienteID] ),
            CALCULATE ( MIN ( Vendas[Data] ), ALL ( 'Calendario' ) ) >= Inicio
        )
    )`},
{area:"Clientes", nome:"Clientes Recorrentes", oque:"Clientes do período que já tinham comprado antes.", codigo:
`Clientes Recorrentes =
[Clientes Ativos] - [Clientes Novos]`},
{area:"Clientes", nome:"Clientes Perdidos", oque:"Clientes sem comprar há mais de 90 dias na data selecionada.", codigo:
`Clientes Perdidos =
VAR Ref = MAX ( 'Calendario'[Data] )
RETURN
    COUNTROWS (
        FILTER (
            ALL ( Cliente[ClienteID] ),
            VAR Ultima =
                CALCULATE (
                    MAX ( Vendas[Data] ),
                    ALL ( 'Calendario' ),
                    'Calendario'[Data] <= Ref
                )
            RETURN
                NOT ISBLANK ( Ultima ) && Ultima < Ref - 90
        )
    )`, dica:"Precisa da tabela Cliente relacionada a Vendas. Ajuste os 90 dias ao ciclo do seu negócio."},
{area:"Clientes", nome:"Receita por Cliente", oque:"Quanto cada cliente ativo gerou, em média.", codigo:
`Receita por Cliente =
DIVIDE ( [Receita], [Clientes Ativos] )`},
{area:"Clientes", nome:"Frequência de Compra", oque:"Quantos pedidos cada cliente fez, em média.", codigo:
`Frequência de Compra =
DIVIDE ( [Pedidos], [Clientes Ativos] )`},
{area:"Clientes", nome:"Dias desde a Última Compra", oque:"Há quantos dias o cliente não compra.", codigo:
`Dias sem Comprar =
VAR Ultima =
    CALCULATE ( MAX ( Vendas[Data] ), ALL ( 'Calendario' ) )
RETURN
    IF ( NOT ISBLANK ( Ultima ), DATEDIFF ( Ultima, TODAY (), DAY ) )`, dica:"Use numa tabela por cliente e ordene do maior para o menor."},
{area:"Clientes", nome:"Taxa de Retenção %", oque:"Dos clientes do mês anterior, quantos voltaram a comprar neste mês.", codigo:
`Retenção % =
VAR ClientesAnteriores =
    CALCULATETABLE (
        VALUES ( Vendas[ClienteID] ),
        DATEADD ( 'Calendario'[Data], -1, MONTH )
    )
VAR ClientesAtuais = VALUES ( Vendas[ClienteID] )
RETURN
    DIVIDE (
        COUNTROWS ( INTERSECT ( ClientesAtuais, ClientesAnteriores ) ),
        COUNTROWS ( ClientesAnteriores )
    )`},

// ---------- Estoque (8) ----------
{area:"Estoque", nome:"Saldo em Estoque", oque:"O saldo na última data com fotografia de estoque. Não soma datas diferentes.", codigo:
`Saldo em Estoque =
CALCULATE (
    SUM ( Estoque[Saldo] ),
    LASTNONBLANK (
        'Calendario'[Data],
        CALCULATE ( SUM ( Estoque[Saldo] ) )
    )
)`, dica:"Estoque é a tabela com o saldo de cada produto por data, ligada à Calendario e ao Produto."},
{area:"Estoque", nome:"Valor em Estoque", oque:"Quanto dinheiro está parado no estoque, a preço de custo.", codigo:
`Valor em Estoque =
SUMX (
    VALUES ( Produto[ProdutoID] ),
    [Saldo em Estoque] * CALCULATE ( MAX ( Produto[CustoUnitario] ) )
)`},
{area:"Estoque", nome:"Giro de Estoque", oque:"Quantas vezes o estoque se renovou no período.", codigo:
`Giro de Estoque =
DIVIDE (
    [Custo],
    AVERAGEX ( VALUES ( 'Calendario'[AnoMes] ), [Valor em Estoque] )
)`},
{area:"Estoque", nome:"Cobertura em Dias", oque:"Para quantos dias o estoque atual dura, no ritmo de venda do período.", codigo:
`Cobertura (dias) =
DIVIDE (
    [Saldo em Estoque],
    DIVIDE ( [Quantidade], COUNTROWS ( VALUES ( 'Calendario'[Data] ) ) )
)`},
{area:"Estoque", nome:"Produtos sem Estoque", oque:"Quantos produtos estão com saldo zerado.", codigo:
`Produtos sem Estoque =
COUNTROWS (
    FILTER ( VALUES ( Produto[ProdutoID] ), [Saldo em Estoque] <= 0 )
)`},
{area:"Estoque", nome:"Ruptura %", oque:"A porcentagem do mix que está em falta.", codigo:
`Ruptura % =
DIVIDE (
    [Produtos sem Estoque],
    COUNTROWS ( VALUES ( Produto[ProdutoID] ) )
)`},
{area:"Estoque", nome:"Produtos Parados", oque:"Produtos com saldo, mas sem nenhuma venda nos últimos 90 dias.", codigo:
`Produtos Parados =
VAR Ref = MAX ( 'Calendario'[Data] )
RETURN
    COUNTROWS (
        FILTER (
            VALUES ( Produto[ProdutoID] ),
            CALCULATE (
                [Quantidade],
                DATESINPERIOD ( 'Calendario'[Data], Ref, -90, DAY )
            ) = 0
                && [Saldo em Estoque] > 0
        )
    )`},
{area:"Estoque", nome:"Necessidade de Compra", oque:"Quanto falta para o produto voltar ao estoque mínimo.", codigo:
`Necessidade de Compra =
MAX ( 0, SUM ( Produto[EstoqueMinimo] ) - [Saldo em Estoque] )`, dica:"Use numa tabela por produto."},

// ---------- RH (8) ----------
{area:"RH", nome:"Headcount", oque:"Quantas pessoas estavam na empresa na data selecionada.", codigo:
`Headcount =
VAR Ref = MAX ( 'Calendario'[Data] )
RETURN
    COUNTROWS (
        FILTER (
            Funcionario,
            Funcionario[DataAdmissao] <= Ref
                && (
                    ISBLANK ( Funcionario[DataDesligamento] )
                        || Funcionario[DataDesligamento] > Ref
                )
        )
    )`, dica:"Deixe a tabela Funcionario sem relacionamento com a Calendario: as datas são comparadas na própria medida."},
{area:"RH", nome:"Admissões", oque:"Quantas pessoas foram contratadas no período.", codigo:
`Admissões =
VAR Inicio = MIN ( 'Calendario'[Data] )
VAR Fim = MAX ( 'Calendario'[Data] )
RETURN
    COUNTROWS (
        FILTER (
            Funcionario,
            Funcionario[DataAdmissao] >= Inicio
                && Funcionario[DataAdmissao] <= Fim
        )
    )`},
{area:"RH", nome:"Desligamentos", oque:"Quantas pessoas saíram no período.", codigo:
`Desligamentos =
VAR Inicio = MIN ( 'Calendario'[Data] )
VAR Fim = MAX ( 'Calendario'[Data] )
RETURN
    COUNTROWS (
        FILTER (
            Funcionario,
            Funcionario[DataDesligamento] >= Inicio
                && Funcionario[DataDesligamento] <= Fim
        )
    )`},
{area:"RH", nome:"Turnover %", oque:"A rotatividade do período, pela fórmula mais usada no Brasil.", codigo:
`Turnover % =
DIVIDE (
    ( [Admissões] + [Desligamentos] ) / 2,
    [Headcount]
)`},
{area:"RH", nome:"Tempo Médio de Casa", oque:"Há quantos anos, em média, as pessoas estão na empresa.", codigo:
`Tempo de Casa (anos) =
VAR Ref = MAX ( 'Calendario'[Data] )
RETURN
    AVERAGEX (
        FILTER (
            Funcionario,
            Funcionario[DataAdmissao] <= Ref
                && (
                    ISBLANK ( Funcionario[DataDesligamento] )
                        || Funcionario[DataDesligamento] > Ref
                )
        ),
        DATEDIFF ( Funcionario[DataAdmissao], Ref, MONTH ) / 12
    )`},
{area:"RH", nome:"Folha Salarial", oque:"A soma dos salários de quem estava na empresa na data selecionada.", codigo:
`Folha Salarial =
VAR Ref = MAX ( 'Calendario'[Data] )
RETURN
    SUMX (
        FILTER (
            Funcionario,
            Funcionario[DataAdmissao] <= Ref
                && (
                    ISBLANK ( Funcionario[DataDesligamento] )
                        || Funcionario[DataDesligamento] > Ref
                )
        ),
        Funcionario[Salario]
    )`},
{area:"RH", nome:"Salário Médio", oque:"A folha dividida pelo número de pessoas.", codigo:
`Salário Médio =
DIVIDE ( [Folha Salarial], [Headcount] )`},
{area:"RH", nome:"Absenteísmo %", oque:"Horas de ausência sobre as horas previstas de trabalho no mês.", codigo:
`Absenteísmo % =
DIVIDE ( SUM ( Ausencias[Horas] ), [Headcount] * 220 )`, dica:"220 h é a jornada mensal de 44 h por semana. Ajuste para a jornada da sua empresa."}
];
