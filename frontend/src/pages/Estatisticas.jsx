import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
    BarChart3,
    Building2,
    TrendingDown,
    MapPin,
    Home,
    DollarSign,
    Layers,
    ArrowUpDown,
    ExternalLink,
    Search,
    MousePointerClick,
    Sparkles,
    Archive,
} from "lucide-react";
import { getEstatisticas } from "../services/api";
import { FILTROS_INICIAIS, salvarFiltrosSalvos, salvarPaginaSalva } from "../components/Filtros";
import { estaAutenticadoCorretor } from "../utils/authCorretor";

const formatarMoeda = (valor) => {
    if (!valor || valor <= 0) return "—";
    return Number(valor).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
        maximumFractionDigits: 0,
    });
};

const formatarMoedaDecimal = (valor) => {
    if (!valor || valor <= 0) return "—";
    return Number(valor).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });
};

const Estatisticas = () => {
    const navigate = useNavigate();
    const [dados, setDados] = useState(null);
    const [loading, setLoading] = useState(true);
    const [erro, setErro] = useState(null);
    const [cidadeSelecionada, setCidadeSelecionada] = useState("São João del Rei");
    const [abaFaixaPreco, setAbaFaixaPreco] = useState("VENDA");
    const [buscaBairro, setBuscaBairro] = useState("");
    const [ordenacaoBairro, setOrdenacaoBairro] = useState("ativos_desc");

    useEffect(() => {
        if (!estaAutenticadoCorretor()) {
            navigate("/corretor/login?redirect=/estatisticas", { replace: true });
            return undefined;
        }

        let ativo = true;
        const carregar = async () => {
            setLoading(true);
            setErro(null);
            try {
                const res = await getEstatisticas(cidadeSelecionada);
                if (ativo) setDados(res);
            } catch (error) {
                console.error(error);
                if (!ativo) return;
                if (error.status === 401) {
                    navigate("/corretor/login?redirect=/estatisticas", { replace: true });
                    return;
                }
                setErro("Não foi possível carregar os indicadores de mercado.");
            } finally {
                if (ativo) setLoading(false);
            }
        };
        void carregar();
        return () => {
            ativo = false;
        };
    }, [cidadeSelecionada, navigate]);

    const navegarComFiltro = (novosFiltros) => {
        const baseFiltros = {
            ...FILTROS_INICIAIS,
            cidade: cidadeSelecionada || "",
            ordenar_por: "recente",
            ...novosFiltros,
        };
        salvarFiltrosSalvos(baseFiltros);
        salvarPaginaSalva(1);
        navigate("/");
    };

    const bairrosFiltrados = useMemo(() => {
        if (!dados?.por_bairro) return [];
        let lista = [...dados.por_bairro];
        if (buscaBairro.trim()) {
            const termo = buscaBairro.toLowerCase().trim();
            lista = lista.filter((b) => b.bairro.toLowerCase().includes(termo));
        }
        lista.sort((a, b) => {
            if (ordenacaoBairro === "m2_venda_desc") return (b.preco_m2_venda || 0) - (a.preco_m2_venda || 0);
            if (ordenacaoBairro === "m2_venda_asc") {
                const va = a.preco_m2_venda > 0 ? a.preco_m2_venda : Number.MAX_SAFE_INTEGER;
                const vb = b.preco_m2_venda > 0 ? b.preco_m2_venda : Number.MAX_SAFE_INTEGER;
                return va - vb;
            }
            if (ordenacaoBairro === "ticket_venda_desc")
                return (b.ticket_medio_venda || 0) - (a.ticket_medio_venda || 0);
            if (ordenacaoBairro === "ticket_aluguel_desc")
                return (b.ticket_medio_aluguel || 0) - (a.ticket_medio_aluguel || 0);
            return b.ativos - a.ativos;
        });
        return lista;
    }, [dados, buscaBairro, ordenacaoBairro]);

    const maiorM2Bairro = useMemo(() => {
        if (!dados?.por_bairro?.length) return 1;
        return Math.max(...dados.por_bairro.map((b) => b.preco_m2_venda || 0), 1);
    }, [dados]);

    const resumo = dados?.resumo_geral || {};
    const faixasAtuais =
        abaFaixaPreco === "VENDA" ? dados?.faixas_venda || [] : dados?.faixas_aluguel || [];
    const totalFaixasAtuais = useMemo(
        () => faixasAtuais.reduce((acc, item) => acc + (item.quantidade || 0), 0),
        [faixasAtuais]
    );

    return (
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {/* Cabeçalho / Filtro de Cidade */}
            <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 rounded-2xl p-6 sm:p-8 text-white shadow-md mb-6">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-5">
                    <div>
                        <div className="inline-flex items-center gap-2 bg-blue-500/20 border border-blue-400/30 text-blue-200 text-xs font-semibold px-3 py-1 rounded-full mb-3">
                            <Sparkles size={13} />
                            Inteligência Imobiliária em Tempo Real
                        </div>
                        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                            Raio-X do Mercado Imobiliário
                        </h1>
                        <p className="text-sm text-slate-300 mt-1.5 max-w-2xl">
                            Indicadores consolidados de preço por m², liquidez de estoque, avaliação por bairro e
                            participação de mercado das imobiliárias monitoradas.
                        </p>
                    </div>

                    <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 shrink-0">
                        <div className="bg-white/10 backdrop-blur-sm border border-white/15 rounded-xl px-3.5 py-2">
                            <label
                                htmlFor="seletor-cidade-estatisticas"
                                className="block text-[10px] font-bold uppercase tracking-wider text-blue-200 mb-0.5"
                            >
                                Recorte Geográfico
                            </label>
                            <div className="flex items-center gap-2">
                                <MapPin size={15} className="text-blue-300 shrink-0" />
                                <select
                                    id="seletor-cidade-estatisticas"
                                    value={cidadeSelecionada}
                                    onChange={(e) => setCidadeSelecionada(e.target.value)}
                                    className="bg-transparent text-white font-semibold text-sm focus:outline-none cursor-pointer pr-2"
                                >
                                    <option value="" className="text-gray-900">
                                        Todas as Cidades da Região
                                    </option>
                                    {dados?.cidades_disponiveis?.map((c) => (
                                        <option key={c.cidade} value={c.cidade} className="text-gray-900">
                                            {c.cidade} ({c.ativos} ativos)
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {erro && (
                <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl mb-6 text-sm font-medium">
                    {erro}
                </div>
            )}

            {loading ? (
                <div className="space-y-6">
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        {[1, 2, 3, 4].map((n) => (
                            <div
                                key={n}
                                className="bg-white rounded-2xl p-5 border border-gray-100 h-36 animate-pulse"
                            >
                                <div className="h-4 bg-gray-200 rounded w-1/2 mb-4" />
                                <div className="h-8 bg-gray-200 rounded w-3/4 mb-3" />
                                <div className="h-3 bg-gray-100 rounded w-2/3" />
                            </div>
                        ))}
                    </div>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="bg-white rounded-2xl p-6 border border-gray-100 h-80 animate-pulse" />
                        <div className="bg-white rounded-2xl p-6 border border-gray-100 h-80 animate-pulse" />
                    </div>
                </div>
            ) : (
                <>
                    {/* KPIs Executivos */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                        {/* Card 1: Estoque & Liquidez */}
                        <div className="bg-white rounded-2xl p-5 border border-gray-200/80 shadow-sm flex flex-col justify-between">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-bold uppercase tracking-wider text-gray-500">
                                    Estoque Ativo
                                </span>
                                <span className="p-2 rounded-xl bg-blue-50 text-blue-600">
                                    <Home size={18} />
                                </span>
                            </div>
                            <div>
                                <div className="flex items-baseline gap-2">
                                    <span className="text-3xl font-extrabold text-gray-900">
                                        {(resumo.total_ativos || 0).toLocaleString("pt-BR")}
                                    </span>
                                    <span className="text-xs font-semibold text-gray-500">anúncios</span>
                                </div>
                                <div className="flex items-center gap-2 mt-2 text-xs text-gray-600">
                                    <span className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-700 font-semibold">
                                        {resumo.ativos_venda || 0} Venda
                                    </span>
                                    <span className="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-700 font-semibold">
                                        {resumo.ativos_aluguel || 0} Aluguel
                                    </span>
                                </div>
                            </div>
                            <div className="mt-3 pt-2.5 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
                                <span className="flex items-center gap-1">
                                    <Archive size={12} className="text-gray-400" />
                                    Histórico absorvido: <strong>{resumo.total_descontinuados || 0}</strong>
                                </span>
                                <span className="font-semibold text-slate-700">
                                    {resumo.taxa_absorcao_pct || 0}% giro
                                </span>
                            </div>
                        </div>

                        {/* Card 2: Valor do Metro Quadrado */}
                        <div className="bg-white rounded-2xl p-5 border border-gray-200/80 shadow-sm flex flex-col justify-between">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-bold uppercase tracking-wider text-gray-500">
                                    Valor Médio do m²
                                </span>
                                <span className="p-2 rounded-xl bg-indigo-50 text-indigo-600">
                                    <Layers size={18} />
                                </span>
                            </div>
                            <div>
                                <div className="flex items-baseline gap-1.5">
                                    <span className="text-2xl sm:text-3xl font-extrabold text-gray-900">
                                        {formatarMoeda(resumo.preco_m2_venda)}
                                    </span>
                                    <span className="text-xs font-semibold text-gray-500">/m² venda</span>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                    Baseado em imóveis com área útil/construída informada
                                </p>
                            </div>
                            <div className="mt-3 pt-2.5 border-t border-gray-100 flex items-center justify-between text-xs">
                                <span className="text-gray-500">Locação por m²:</span>
                                <span className="font-bold text-indigo-700">
                                    {resumo.preco_m2_aluguel > 0
                                        ? `${formatarMoedaDecimal(resumo.preco_m2_aluguel)}/m²`
                                        : "—"}
                                </span>
                            </div>
                        </div>

                        {/* Card 3: Ticket Médio e Mediana Venda */}
                        <div className="bg-white rounded-2xl p-5 border border-gray-200/80 shadow-sm flex flex-col justify-between">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-bold uppercase tracking-wider text-gray-500">
                                    Ticket de Venda
                                </span>
                                <span className="p-2 rounded-xl bg-emerald-50 text-emerald-600">
                                    <DollarSign size={18} />
                                </span>
                            </div>
                            <div>
                                <div className="text-2xl sm:text-3xl font-extrabold text-gray-900">
                                    {formatarMoeda(resumo.mediana_venda)}
                                </div>
                                <span className="text-xs text-emerald-700 font-semibold">
                                    Valor Mediano de Venda
                                </span>
                            </div>
                            <div className="mt-3 pt-2.5 border-t border-gray-100 flex items-center justify-between text-xs">
                                <span className="text-gray-500">Média aritmética:</span>
                                <span className="font-semibold text-gray-800">
                                    {formatarMoeda(resumo.ticket_medio_venda)}
                                </span>
                            </div>
                        </div>

                        {/* Card 4: Aluguel & Oportunidades */}
                        <div className="bg-white rounded-2xl p-5 border border-gray-200/80 shadow-sm flex flex-col justify-between">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-xs font-bold uppercase tracking-wider text-gray-500">
                                    Locação & Oportunidades
                                </span>
                                <span className="p-2 rounded-xl bg-amber-50 text-amber-600">
                                    <TrendingDown size={18} />
                                </span>
                            </div>
                            <div>
                                <div className="flex items-baseline gap-2">
                                    <span className="text-2xl sm:text-3xl font-extrabold text-gray-900">
                                        {formatarMoeda(resumo.mediana_aluguel)}
                                    </span>
                                    <span className="text-xs font-semibold text-gray-500">/mês mediano</span>
                                </div>
                                <p className="text-xs text-gray-500 mt-1">
                                    Média locação: <strong>{formatarMoeda(resumo.ticket_medio_aluguel)}</strong>
                                </p>
                            </div>
                            <div className="mt-3 pt-2.5 border-t border-gray-100 flex items-center justify-between text-xs">
                                <button
                                    type="button"
                                    onClick={() => navegarComFiltro({ apenas_queda_preco: true })}
                                    className="inline-flex items-center gap-1 text-emerald-700 hover:text-emerald-800 font-bold hover:underline"
                                >
                                    <TrendingDown size={13} />
                                    {resumo.total_com_queda_preco || 0} com queda de preço
                                </button>
                                <span className="text-gray-500 flex items-center gap-1">
                                    <MousePointerClick size={12} />
                                    {resumo.total_cliques || 0} leads
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Grid: Tipos de Imóvel + Faixas de Preço */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                        {/* Distribuição por Tipo de Imóvel */}
                        <div className="bg-white rounded-2xl border border-gray-200/80 shadow-sm p-6">
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                                        <BarChart3 size={18} className="text-blue-600" />
                                        Estoque e Preço por Tipologia
                                    </h2>
                                    <p className="text-xs text-gray-500 mt-0.5">
                                        Clique em um tipo de imóvel para explorar os anúncios ativos
                                    </p>
                                </div>
                            </div>

                            <div className="space-y-3.5">
                                {dados?.por_tipo?.map((item) => (
                                    <button
                                        type="button"
                                        key={item.tipo}
                                        onClick={() => navegarComFiltro({ tipo: item.tipo })}
                                        className="w-full text-left group p-3 rounded-xl border border-gray-100 hover:border-blue-200 hover:bg-blue-50/30 transition-all cursor-pointer"
                                    >
                                        <div className="flex items-center justify-between text-sm mb-1.5">
                                            <div className="flex items-center gap-2">
                                                <span className="font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                                                    {item.tipo}
                                                </span>
                                                <span className="text-xs font-semibold text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full">
                                                    {item.ativos} ({item.percentual}%)
                                                </span>
                                            </div>
                                            <div className="text-xs text-right">
                                                {item.preco_m2_venda > 0 && (
                                                    <span className="font-semibold text-indigo-700 mr-3">
                                                        {formatarMoeda(item.preco_m2_venda)}/m²
                                                    </span>
                                                )}
                                                <span className="text-gray-600">
                                                    Média:{" "}
                                                    <strong className="text-gray-900">
                                                        {formatarMoeda(item.ticket_medio_venda)}
                                                    </strong>
                                                </span>
                                            </div>
                                        </div>

                                        <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-blue-600 rounded-full transition-all duration-500"
                                                style={{ width: `${Math.max(item.percentual, 2)}%` }}
                                            />
                                        </div>

                                        <div className="flex items-center justify-between mt-1.5 text-[11px] text-gray-500">
                                            <span>
                                                {item.venda} à venda · {item.aluguel} para alugar
                                            </span>
                                            {item.ticket_medio_aluguel > 0 && (
                                                <span>
                                                    Aluguel médio: {formatarMoeda(item.ticket_medio_aluguel)}
                                                </span>
                                            )}
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Pirâmide de Faixas de Preço */}
                        <div className="bg-white rounded-2xl border border-gray-200/80 shadow-sm p-6 flex flex-col justify-between">
                            <div>
                                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-5">
                                    <div>
                                        <h2 className="text-base font-bold text-gray-900 flex items-center gap-2">
                                            <DollarSign size={18} className="text-emerald-600" />
                                            Distribuição por Faixa de Valor
                                        </h2>
                                        <p className="text-xs text-gray-500 mt-0.5">
                                            Concentração da oferta ativa por faixa de orçamento
                                        </p>
                                    </div>

                                    <div className="inline-flex rounded-xl bg-gray-100 p-1 self-start">
                                        <button
                                            type="button"
                                            onClick={() => setAbaFaixaPreco("VENDA")}
                                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                                                abaFaixaPreco === "VENDA"
                                                    ? "bg-white text-blue-600 shadow-sm"
                                                    : "text-gray-600 hover:text-gray-900"
                                            }`}
                                        >
                                            Venda
                                        </button>
                                        <button
                                            type="button"
                                            onClick={() => setAbaFaixaPreco("ALUGUEL")}
                                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                                                abaFaixaPreco === "ALUGUEL"
                                                    ? "bg-white text-emerald-600 shadow-sm"
                                                    : "text-gray-600 hover:text-gray-900"
                                            }`}
                                        >
                                            Aluguel
                                        </button>
                                    </div>
                                </div>

                                <div className="space-y-4 mt-2">
                                    {faixasAtuais.map((f) => {
                                        const pct =
                                            totalFaixasAtuais > 0
                                                ? Math.round((f.quantidade / totalFaixasAtuais) * 1000) / 10
                                                : 0;
                                        return (
                                            <div key={f.faixa} className="space-y-1.5">
                                                <div className="flex items-center justify-between text-xs">
                                                    <span className="font-semibold text-gray-700">{f.faixa}</span>
                                                    <span className="font-bold text-gray-900">
                                                        {f.quantidade.toLocaleString("pt-BR")} imóveis{" "}
                                                        <span className="text-gray-400 font-normal">({pct}%)</span>
                                                    </span>
                                                </div>
                                                <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
                                                    <div
                                                        className={`h-full rounded-full transition-all duration-500 ${
                                                            abaFaixaPreco === "VENDA"
                                                                ? "bg-gradient-to-r from-blue-500 to-indigo-600"
                                                                : "bg-gradient-to-r from-emerald-500 to-teal-600"
                                                        }`}
                                                        style={{ width: `${Math.max(pct, 2)}%` }}
                                                    />
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>

                            <div className="mt-6 pt-4 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
                                <span>
                                    Total analisado com preço divulgado:{" "}
                                    <strong className="text-gray-800">{totalFaixasAtuais}</strong>
                                </span>
                                <button
                                    type="button"
                                    onClick={() => navegarComFiltro({ modalidade: abaFaixaPreco })}
                                    className="text-blue-600 hover:text-blue-700 font-semibold inline-flex items-center gap-1"
                                >
                                    Explorar catálogo de {abaFaixaPreco.toLowerCase()}
                                    <ExternalLink size={12} />
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Ranking de Valorização por Bairro */}
                    <div className="bg-white rounded-2xl border border-gray-200/80 shadow-sm p-6 mb-6">
                        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-5">
                            <div>
                                <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                    <MapPin size={19} className="text-blue-600" />
                                    Mapa de Valorização por Bairro
                                </h2>
                                <p className="text-xs text-gray-500 mt-0.5">
                                    Comparativo de preço do metro quadrado, ticket médio de venda/locação e liquidez
                                    por bairro (mínimo de 2 imóveis ativos)
                                </p>
                            </div>

                            <div className="flex flex-col sm:flex-row gap-2.5">
                                <div className="relative">
                                    <Search
                                        size={14}
                                        className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                                    />
                                    <input
                                        type="text"
                                        value={buscaBairro}
                                        onChange={(e) => setBuscaBairro(e.target.value)}
                                        placeholder="Filtrar bairro..."
                                        className="pl-8 pr-3 py-2 text-xs bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 w-full sm:w-48"
                                    />
                                </div>

                                <div className="flex items-center gap-1.5 bg-gray-50 border border-gray-200 rounded-xl px-3 py-2">
                                    <ArrowUpDown size={13} className="text-gray-400 shrink-0" />
                                    <select
                                        value={ordenacaoBairro}
                                        onChange={(e) => setOrdenacaoBairro(e.target.value)}
                                        className="bg-transparent text-xs font-semibold text-gray-700 focus:outline-none cursor-pointer"
                                    >
                                        <option value="ativos_desc">Maior Estoque Ativo</option>
                                        <option value="m2_venda_desc">Maior Valor do m² (Venda)</option>
                                        <option value="m2_venda_asc">Menor Valor do m² (Oportunidade)</option>
                                        <option value="ticket_venda_desc">Maior Ticket Médio (Venda)</option>
                                        <option value="ticket_aluguel_desc">Maior Aluguel Médio</option>
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="border-b border-gray-200 text-[11px] font-bold uppercase tracking-wider text-gray-400">
                                        <th className="py-3 pr-4">Bairro</th>
                                        <th className="py-3 px-3 text-center">Oferta (Venda / Aluguel)</th>
                                        <th className="py-3 px-3">Valor Médio do m²</th>
                                        <th className="py-3 px-3 text-right">Ticket Médio Venda</th>
                                        <th className="py-3 px-3 text-right">Aluguel Médio</th>
                                        <th className="py-3 pl-3 text-right">Ação</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100 text-sm">
                                    {bairrosFiltrados.length === 0 ? (
                                        <tr>
                                            <td colSpan={6} className="py-8 text-center text-gray-400 text-xs">
                                                Nenhum bairro encontrado com os critérios selecionados.
                                            </td>
                                        </tr>
                                    ) : (
                                        bairrosFiltrados.map((b, idx) => {
                                            const pctM2 =
                                                b.preco_m2_venda > 0
                                                    ? Math.min(
                                                          100,
                                                          Math.max(
                                                              8,
                                                              Math.round((b.preco_m2_venda / maiorM2Bairro) * 100)
                                                          )
                                                      )
                                                    : 0;
                                            return (
                                                <tr
                                                    key={b.bairro}
                                                    className="hover:bg-blue-50/40 transition-colors group"
                                                >
                                                    <td className="py-3 pr-4">
                                                        <div className="flex items-center gap-2.5">
                                                            <span className="w-6 h-6 rounded-lg bg-gray-100 text-gray-500 text-xs font-bold flex items-center justify-center shrink-0">
                                                                {idx + 1}
                                                            </span>
                                                            <div>
                                                                <span className="font-bold text-gray-900 block">
                                                                    {b.bairro}
                                                                </span>
                                                                {b.descontinuados > 0 && (
                                                                    <span className="text-[11px] text-gray-400">
                                                                        {b.descontinuados} absorvidos no histórico
                                                                    </span>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="py-3 px-3 text-center">
                                                        <span className="font-bold text-gray-900">{b.ativos}</span>
                                                        <span className="text-xs text-gray-400 ml-1">
                                                            ({b.venda}V / {b.aluguel}A)
                                                        </span>
                                                    </td>
                                                    <td className="py-3 px-3 min-w-[180px]">
                                                        {b.preco_m2_venda > 0 ? (
                                                            <div>
                                                                <div className="flex items-center justify-between text-xs mb-1">
                                                                    <span className="font-bold text-indigo-700">
                                                                        {formatarMoeda(b.preco_m2_venda)}/m²
                                                                    </span>
                                                                </div>
                                                                <div className="w-full h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                                                    <div
                                                                        className="h-full bg-indigo-500 rounded-full"
                                                                        style={{ width: `${pctM2}%` }}
                                                                    />
                                                                </div>
                                                            </div>
                                                        ) : (
                                                            <span className="text-xs text-gray-400">Sem área inf.</span>
                                                        )}
                                                    </td>
                                                    <td className="py-3 px-3 text-right font-semibold text-gray-800">
                                                        {formatarMoeda(b.ticket_medio_venda)}
                                                    </td>
                                                    <td className="py-3 px-3 text-right font-medium text-gray-600">
                                                        {formatarMoeda(b.ticket_medio_aluguel)}
                                                    </td>
                                                    <td className="py-3 pl-3 text-right">
                                                        <button
                                                            type="button"
                                                            onClick={() => navegarComFiltro({ bairro: b.bairro })}
                                                            className="text-xs font-bold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded-lg transition-colors inline-flex items-center gap-1"
                                                        >
                                                            Ver imóveis
                                                            <ExternalLink size={11} />
                                                        </button>
                                                    </td>
                                                </tr>
                                            );
                                        })
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Market Share das Imobiliárias e Leads B2B */}
                    <div className="bg-white rounded-2xl border border-gray-200/80 shadow-sm p-6">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-5">
                            <div>
                                <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                    <Building2 size={19} className="text-blue-600" />
                                    Market Share & Desempenho por Imobiliária
                                </h2>
                                <p className="text-xs text-gray-500 mt-0.5">
                                    Participação sobre o estoque ativo, perfil de carteira e leads (cliques
                                    qualificados) gerados pela plataforma
                                </p>
                            </div>
                            <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-3 py-1 rounded-full self-start">
                                {resumo.total_imobiliarias_ativas || 0} imobiliárias ativas
                            </span>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="border-b border-gray-200 text-[11px] font-bold uppercase tracking-wider text-gray-400">
                                        <th className="py-3 pr-4">Imobiliária</th>
                                        <th className="py-3 px-3">Market Share (Estoque Ativo)</th>
                                        <th className="py-3 px-3 text-center">Carteira (Venda / Aluguel)</th>
                                        <th className="py-3 px-3 text-right">Ticket Médio Venda</th>
                                        <th className="py-3 px-3 text-right">Ticket Médio Aluguel</th>
                                        <th className="py-3 px-3 text-center">Leads Gerados</th>
                                        <th className="py-3 pl-3 text-right">Catálogo</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100 text-sm">
                                    {dados?.por_imobiliaria?.map((imob) => (
                                        <tr key={imob.imobiliaria} className="hover:bg-gray-50 transition-colors">
                                            <td className="py-3.5 pr-4">
                                                <span className="font-bold text-gray-900 block">
                                                    {imob.imobiliaria}
                                                </span>
                                                {imob.descontinuados > 0 && (
                                                    <span className="text-[11px] text-gray-400">
                                                        {imob.descontinuados} encerrados/vendidos
                                                    </span>
                                                )}
                                            </td>
                                            <td className="py-3.5 px-3 min-w-[190px]">
                                                <div className="flex items-center justify-between text-xs mb-1">
                                                    <span className="font-bold text-gray-900">
                                                        {imob.ativos} imóveis
                                                    </span>
                                                    <span className="font-semibold text-blue-600">
                                                        {imob.market_share_pct}%
                                                    </span>
                                                </div>
                                                <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-blue-600 rounded-full"
                                                        style={{
                                                            width: `${Math.max(imob.market_share_pct, 2)}%`,
                                                        }}
                                                    />
                                                </div>
                                            </td>
                                            <td className="py-3.5 px-3 text-center text-xs">
                                                <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-semibold mr-1">
                                                    {imob.venda} Venda
                                                </span>
                                                <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-semibold">
                                                    {imob.aluguel} Aluguel
                                                </span>
                                            </td>
                                            <td className="py-3.5 px-3 text-right font-semibold text-gray-800">
                                                {formatarMoeda(imob.ticket_medio_venda)}
                                            </td>
                                            <td className="py-3.5 px-3 text-right text-gray-600">
                                                {formatarMoeda(imob.ticket_medio_aluguel)}
                                            </td>
                                            <td className="py-3.5 px-3 text-center">
                                                <span
                                                    className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold ${
                                                        imob.cliques > 0
                                                            ? "bg-emerald-50 text-emerald-700"
                                                            : "bg-gray-100 text-gray-500"
                                                    }`}
                                                >
                                                    <MousePointerClick size={12} />
                                                    {imob.cliques || 0}
                                                </span>
                                            </td>
                                            <td className="py-3.5 pl-3 text-right">
                                                <button
                                                    type="button"
                                                    onClick={() =>
                                                        navegarComFiltro({ imobiliaria: imob.imobiliaria })
                                                    }
                                                    className="text-xs font-bold text-blue-600 hover:text-blue-800 hover:underline inline-flex items-center gap-1"
                                                >
                                                    Filtrar
                                                    <ExternalLink size={11} />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};

export default Estatisticas;

