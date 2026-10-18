import { useState, useEffect, useMemo } from 'react';
import {
    SearchX,
    SlidersHorizontal,
    ArrowUpDown,
    X,
    ChevronLeft,
    ChevronRight,
} from 'lucide-react';
import ImovelCard from '../components/ImovelCard';
import Filtros, { FILTROS_INICIAIS } from '../components/Filtros';
import { getImoveis, getFiltros } from '../services/api';

const Home = () => {
    const [filtros, setFiltros] = useState(() => {
        try {
            const salvos = sessionStorage.getItem('crawty_filtros');
            if (!salvos) return FILTROS_INICIAIS;
            const parsed = { ...FILTROS_INICIAIS, ...JSON.parse(salvos) };
            if (parsed.ordenar_por === 'recentes') {
                parsed.ordenar_por = 'recente';
            }
            return parsed;
        } catch {
            return FILTROS_INICIAIS;
        }
    });

    const [meta, setMeta] = useState(() => {
        const paginaSalva = sessionStorage.getItem('crawty_page');
        return {
            total: 0,
            page: paginaSalva ? parseInt(paginaSalva, 10) : 1,
            pages: 1,
        };
    });

    const [imoveis, setImoveis] = useState([]);
    const [opcoesFiltro, setOpcoesFiltro] = useState({
        cidades: [],
        bairros: [],
        bairros_por_cidade: {},
        tipos: [],
        subtipos: [],
        subtipos_por_tipo: {},
        imobiliarias: [],
    });
    const [loading, setLoading] = useState(true);
    const [erro, setErro] = useState(false);
    const [abertoMobile, setAbertoMobile] = useState(false);

    // Salva no SessionStorage sempre que Filtros ou Página mudarem
    useEffect(() => {
        sessionStorage.setItem('crawty_filtros', JSON.stringify(filtros));
        sessionStorage.setItem('crawty_page', meta.page.toString());
    }, [filtros, meta.page]);

    // Recarrega as opções de filtro quando o status (ativos/descontinuados/todos) mudar
    useEffect(() => {
        getFiltros(filtros.status || 'ativos').then((data) => setOpcoesFiltro(data));
    }, [filtros.status]);

    // Carregar imóveis com debounce
    useEffect(() => {
        const fetchDados = async () => {
            setLoading(true);
            setErro(false);
            try {
                const dados = await getImoveis({
                    page: meta.page,
                    limit: 12,
                    ...filtros,
                });
                setImoveis(dados.data || []);
                setMeta((prev) => ({ ...dados.meta, page: prev.page }));
            } catch (error) {
                console.error(error);
                setErro(true);
                setImoveis([]);
            } finally {
                setLoading(false);
            }
        };
        const timeoutId = setTimeout(fetchDados, 280);
        return () => clearTimeout(timeoutId);
    }, [filtros, meta.page]);

    const handleFiltrosChange = (novoEstadoOuFuncao) => {
        setFiltros((prev) => {
            const novosFiltros =
                typeof novoEstadoOuFuncao === 'function'
                    ? novoEstadoOuFuncao(prev)
                    : novoEstadoOuFuncao;

            if (JSON.stringify(prev) !== JSON.stringify(novosFiltros)) {
                setMeta((m) => ({ ...m, page: 1 }));
            }
            return novosFiltros;
        });
    };

    const limparFiltros = () => {
        handleFiltrosChange({ ...FILTROS_INICIAIS, ordenar_por: filtros.ordenar_por });
    };

    const removerFiltroIndividual = (chave) => {
        handleFiltrosChange((prev) => ({
            ...prev,
            [chave]:
                chave === 'status'
                    ? 'ativos'
                    : chave === 'apenas_com_foto' || chave === 'apenas_queda_preco'
                    ? false
                    : '',
        }));
    };

    const mudarPagina = (novaPagina) => {
        setMeta((prev) => ({ ...prev, page: novaPagina }));
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    // Monta chips visuais dos filtros ativos
    const chipsAtivos = useMemo(() => {
        const chips = [];
        if (filtros.modalidade) {
            chips.push({
                key: 'modalidade',
                label: filtros.modalidade === 'VENDA' ? 'Comprar' : 'Alugar',
            });
        }
        if (filtros.busca) chips.push({ key: 'busca', label: `"${filtros.busca}"` });
        if (filtros.cidade) chips.push({ key: 'cidade', label: filtros.cidade });
        if (filtros.bairro) chips.push({ key: 'bairro', label: `Bairro: ${filtros.bairro}` });
        if (filtros.tipo) chips.push({ key: 'tipo', label: filtros.tipo });
        if (filtros.subtipo) chips.push({ key: 'subtipo', label: filtros.subtipo });
        if (filtros.imobiliaria) chips.push({ key: 'imobiliaria', label: filtros.imobiliaria });
        if (filtros.preco_min) {
            chips.push({
                key: 'preco_min',
                label: `Mín R$ ${Number(filtros.preco_min).toLocaleString('pt-BR')}`,
            });
        }
        if (filtros.preco_max) {
            chips.push({
                key: 'preco_max',
                label: `Máx R$ ${Number(filtros.preco_max).toLocaleString('pt-BR')}`,
            });
        }
        if (filtros.quartos_min)
            chips.push({ key: 'quartos_min', label: `${filtros.quartos_min}+ quartos` });
        if (filtros.suites_min)
            chips.push({ key: 'suites_min', label: `${filtros.suites_min}+ suítes` });
        if (filtros.banheiros_min)
            chips.push({ key: 'banheiros_min', label: `${filtros.banheiros_min}+ banheiros` });
        if (filtros.vagas_min)
            chips.push({ key: 'vagas_min', label: `${filtros.vagas_min}+ vagas` });
        if (filtros.area_min)
            chips.push({ key: 'area_min', label: `Área mín ${filtros.area_min} m²` });
        if (filtros.area_max)
            chips.push({ key: 'area_max', label: `Área máx ${filtros.area_max} m²` });
        if (filtros.apenas_com_foto)
            chips.push({ key: 'apenas_com_foto', label: 'Com fotos' });
        if (filtros.apenas_queda_preco)
            chips.push({ key: 'apenas_queda_preco', label: 'Redução de preço' });
        if (filtros.status && filtros.status !== 'ativos') {
            chips.push({
                key: 'status',
                label: filtros.status === 'descontinuados' ? 'Inativos / Histórico' : 'Todos os status',
            });
        }
        return chips;
    }, [filtros]);

    // Páginas visíveis na barra de paginação
    const paginasVisiveis = useMemo(() => {
        const totalPaginas = meta.pages || 1;
        const atual = meta.page || 1;
        const delta = 2;
        const inicio = Math.max(1, atual - delta);
        const fim = Math.min(totalPaginas, atual + delta);
        const lista = [];
        for (let i = inicio; i <= fim; i++) {
            lista.push(i);
        }
        return lista;
    }, [meta.page, meta.pages]);

    return (
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex flex-col lg:flex-row gap-7 items-start">
                {/* Sidebar de Filtros (Desktop) + Drawer (Mobile) */}
                <Filtros
                    opcoes={opcoesFiltro}
                    filtros={filtros}
                    setFiltros={handleFiltrosChange}
                    onLimpar={limparFiltros}
                    abertoMobile={abertoMobile}
                    setAbertoMobile={setAbertoMobile}
                    totalResultados={meta.total}
                />

                {/* Conteúdo Principal */}
                <main className="flex-1 w-full min-w-0">
                    {/* Barra Superior de Resultados e Ordenação */}
                    <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm mb-5">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                            <div className="flex items-center justify-between sm:justify-start gap-3">
                                {/* Botão Filtrar no Mobile */}
                                <button
                                    type="button"
                                    onClick={() => setAbertoMobile(true)}
                                    className="lg:hidden flex items-center gap-2 px-3.5 py-2 bg-blue-600 text-white rounded-xl text-xs font-bold shadow-sm"
                                >
                                    <SlidersHorizontal size={15} />
                                    Filtros
                                    {chipsAtivos.length > 0 && (
                                        <span className="bg-white text-blue-600 px-1.5 py-0.5 rounded-full text-[10px]">
                                            {chipsAtivos.length}
                                        </span>
                                    )}
                                </button>

                                <div>
                                    <h2 className="text-gray-900 font-bold text-base sm:text-lg leading-tight">
                                        {filtros.tipo || 'Imóveis'}{' '}
                                        {filtros.modalidade === 'VENDA'
                                            ? 'à venda'
                                            : filtros.modalidade === 'ALUGUEL'
                                            ? 'para alugar'
                                            : 'disponíveis'}
                                        {filtros.cidade ? ` em ${filtros.cidade}` : ''}
                                    </h2>
                                    <p className="text-xs text-gray-500">
                                        {loading
                                            ? 'Buscando imóveis...'
                                            : `${meta.total.toLocaleString('pt-BR')} imóvel(is) encontrado(s)`}
                                    </p>
                                </div>
                            </div>

                            {/* Seletor de Ordenação */}
                            <div className="flex items-center gap-2 self-end sm:self-auto">
                                <ArrowUpDown size={15} className="text-gray-400 shrink-0" />
                                <span className="text-xs font-semibold text-gray-500 whitespace-nowrap">
                                    Ordenar por:
                                </span>
                                <select
                                    value={filtros.ordenar_por}
                                    onChange={(e) =>
                                        handleFiltrosChange((prev) => ({
                                            ...prev,
                                            ordenar_por: e.target.value,
                                        }))
                                    }
                                    className="px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-xl text-xs font-semibold text-gray-700 focus:bg-white focus:border-blue-600 outline-none"
                                >
                                    <option value="">Padrão (Relevância)</option>
                                    <option value="menor_preco">Menor Preço</option>
                                    <option value="maior_preco">Maior Preço</option>
                                    <option value="maior_area">Maior Área (m²)</option>
                                    <option value="menor_area">Menor Área (m²)</option>
                                    <option value="recente">Mais Recentes</option>
                                </select>
                            </div>
                        </div>

                        {/* Chips de Filtros Ativos */}
                        {chipsAtivos.length > 0 && (
                            <div className="flex flex-wrap items-center gap-1.5 mt-3.5 pt-3 border-t border-gray-100">
                                {chipsAtivos.map((chip) => (
                                    <span
                                        key={chip.key}
                                        className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200/70"
                                    >
                                        {chip.label}
                                        <button
                                            type="button"
                                            onClick={() => removerFiltroIndividual(chip.key)}
                                            className="hover:text-blue-900 rounded-full p-0.5"
                                            title="Remover filtro"
                                        >
                                            <X size={12} />
                                        </button>
                                    </span>
                                ))}
                                <button
                                    type="button"
                                    onClick={limparFiltros}
                                    className="text-xs font-semibold text-gray-500 hover:text-red-600 ml-2 transition-colors"
                                >
                                    Limpar todos
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Grid de Resultados */}
                    {loading ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                            {[...Array(9)].map((_, i) => (
                                <div
                                    key={i}
                                    className="bg-white rounded-2xl h-[410px] animate-pulse border border-gray-100 overflow-hidden"
                                >
                                    <div className="h-52 bg-gray-200"></div>
                                    <div className="p-4 space-y-3">
                                        <div className="h-5 bg-gray-200 rounded w-3/4"></div>
                                        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                                        <div className="grid grid-cols-4 gap-2 pt-2">
                                            <div className="h-12 bg-gray-100 rounded-xl"></div>
                                            <div className="h-12 bg-gray-100 rounded-xl"></div>
                                            <div className="h-12 bg-gray-100 rounded-xl"></div>
                                            <div className="h-12 bg-gray-100 rounded-xl"></div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : erro ? (
                        <div className="text-center py-20 bg-white rounded-2xl border border-red-100 border-dashed">
                            <SearchX size={56} className="mx-auto text-red-400 mb-4" />
                            <h3 className="text-lg font-bold text-gray-900 mb-1">
                                Erro de Conexão com a API
                            </h3>
                            <p className="text-sm text-gray-500">
                                Não foi possível carregar os imóveis. Verifique se o backend está em
                                execução.
                            </p>
                        </div>
                    ) : imoveis.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                            {imoveis.map((imovel) => (
                                <ImovelCard key={imovel.id_unico} imovel={imovel} />
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-20 bg-white rounded-2xl border border-gray-200 border-dashed">
                            <SearchX size={56} className="mx-auto text-gray-300 mb-4" />
                            <h3 className="text-lg font-bold text-gray-900 mb-1">
                                Nenhum imóvel encontrado
                            </h3>
                            <p className="text-sm text-gray-500 mb-4">
                                Não encontramos imóveis com essa combinação exata de filtros.
                            </p>
                            <button
                                type="button"
                                onClick={limparFiltros}
                                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-colors"
                            >
                                Limpar todos os filtros
                            </button>
                        </div>
                    )}

                    {/* Paginação Aprimorada */}
                    {!loading && meta.pages > 1 && (
                        <div className="mt-10 flex flex-wrap justify-center items-center gap-2">
                            <button
                                onClick={() => mudarPagina(meta.page - 1)}
                                disabled={meta.page === 1}
                                className="flex items-center gap-1 px-3.5 py-2 bg-white border border-gray-200 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:pointer-events-none transition-colors"
                            >
                                <ChevronLeft size={15} /> Anterior
                            </button>

                            {paginasVisiveis[0] > 1 && (
                                <>
                                    <button
                                        onClick={() => mudarPagina(1)}
                                        className="w-9 h-9 rounded-xl text-xs font-semibold bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
                                    >
                                        1
                                    </button>
                                    {paginasVisiveis[0] > 2 && (
                                        <span className="text-gray-400 px-1">...</span>
                                    )}
                                </>
                            )}

                            {paginasVisiveis.map((num) => (
                                <button
                                    key={num}
                                    onClick={() => mudarPagina(num)}
                                    className={`w-9 h-9 rounded-xl text-xs font-bold border transition-all ${
                                        meta.page === num
                                            ? 'bg-blue-600 text-white border-blue-600 shadow-xs'
                                            : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                                    }`}
                                >
                                    {num}
                                </button>
                            ))}

                            {paginasVisiveis[paginasVisiveis.length - 1] < meta.pages && (
                                <>
                                    {paginasVisiveis[paginasVisiveis.length - 1] <
                                        meta.pages - 1 && (
                                        <span className="text-gray-400 px-1">...</span>
                                    )}
                                    <button
                                        onClick={() => mudarPagina(meta.pages)}
                                        className="w-9 h-9 rounded-xl text-xs font-semibold bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
                                    >
                                        {meta.pages}
                                    </button>
                                </>
                            )}

                            <button
                                onClick={() => mudarPagina(meta.page + 1)}
                                disabled={meta.page === meta.pages}
                                className="flex items-center gap-1 px-3.5 py-2 bg-white border border-gray-200 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:pointer-events-none transition-colors"
                            >
                                Próxima <ChevronRight size={15} />
                            </button>
                        </div>
                    )}
                </main>
            </div>
        </div>
    );
};

export default Home;