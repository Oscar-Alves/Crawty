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
import Filtros, {
    FILTROS_INICIAIS,
    obterFiltrosSalvos,
    salvarFiltrosSalvos,
    obterPaginaSalva,
    salvarPaginaSalva,
} from '../components/Filtros';
import { getImoveis, getFiltros } from '../services/api';

const SKELETON_IDS = ['sk-1', 'sk-2', 'sk-3', 'sk-4', 'sk-5', 'sk-6', 'sk-7', 'sk-8', 'sk-9'];

const obterValorPadraoCampo = (chave) => {
    if (chave === 'status') return 'ativos';
    if (chave === 'apenas_com_foto' || chave === 'apenas_queda_preco') return false;
    return '';
};

const obterSufixoModalidadeTitulo = (modalidade) => {
    if (modalidade === 'VENDA') return 'à venda';
    if (modalidade === 'ALUGUEL') return 'para alugar';
    return 'disponíveis';
};

const construirChipsFiltrosAtivos = (filtros) => {
    const chips = [];

    if (filtros.modalidade) {
        chips.push({
            key: 'modalidade',
            label: filtros.modalidade === 'VENDA' ? 'Comprar' : 'Alugar',
        });
    }

    const camposSimples = [
        ['busca', (v) => `"${v}"`],
        ['cidade', (v) => v],
        ['bairro', (v) => `Bairro: ${v}`],
        ['tipo', (v) => v],
        ['subtipo', (v) => v],
        ['imobiliaria', (v) => v],
        ['preco_min', (v) => `Mín R$ ${Number(v).toLocaleString('pt-BR')}`],
        ['preco_max', (v) => `Máx R$ ${Number(v).toLocaleString('pt-BR')}`],
        ['quartos_min', (v) => `${v}+ quartos`],
        ['suites_min', (v) => `${v}+ suítes`],
        ['banheiros_min', (v) => `${v}+ banheiros`],
        ['vagas_min', (v) => `${v}+ vagas`],
        ['area_min', (v) => `Área mín ${v} m²`],
        ['area_max', (v) => `Área máx ${v} m²`],
    ];

    for (const [key, formatar] of camposSimples) {
        if (filtros[key]) {
            chips.push({ key, label: formatar(filtros[key]) });
        }
    }

    if (filtros.apenas_com_foto) {
        chips.push({ key: 'apenas_com_foto', label: 'Com fotos' });
    }
    if (filtros.apenas_queda_preco) {
        chips.push({ key: 'apenas_queda_preco', label: 'Redução de preço' });
    }
    if (filtros.status && filtros.status !== 'ativos') {
        const labelStatus =
            filtros.status === 'descontinuados' ? 'Inativos / Histórico' : 'Todos os status';
        chips.push({ key: 'status', label: labelStatus });
    }

    return chips;
};

const GradeResultadosImoveis = ({ loading, erro, imoveis, onLimparFiltros }) => {
    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {SKELETON_IDS.map((skId) => (
                    <div
                        key={skId}
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
        );
    }

    if (erro) {
        return (
            <div className="text-center py-20 bg-white rounded-2xl border border-red-100 border-dashed">
                <SearchX size={56} className="mx-auto text-red-400 mb-4" />
                <h3 className="text-lg font-bold text-gray-900 mb-1">Erro de Conexão com a API</h3>
                <p className="text-sm text-gray-500">
                    Não foi possível carregar os imóveis. Verifique se o backend está em execução.
                </p>
            </div>
        );
    }

    if (imoveis.length > 0) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {imoveis.map((imovel) => (
                    <ImovelCard key={imovel.id_unico} imovel={imovel} />
                ))}
            </div>
        );
    }

    return (
        <div className="text-center py-20 bg-white rounded-2xl border border-gray-200 border-dashed">
            <SearchX size={56} className="mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-bold text-gray-900 mb-1">Nenhum imóvel encontrado</h3>
            <p className="text-sm text-gray-500 mb-4">
                Não encontramos imóveis com essa combinação exata de filtros.
            </p>
            <button
                type="button"
                onClick={onLimparFiltros}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-colors"
            >
                Limpar todos os filtros
            </button>
        </div>
    );
};

const Home = () => {
    const [filtros, setFiltros] = useState(() => obterFiltrosSalvos());

    const [meta, setMeta] = useState(() => ({
        total: 0,
        page: obterPaginaSalva(),
        pages: 1,
    }));

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

    useEffect(() => {
        salvarFiltrosSalvos(filtros);
        salvarPaginaSalva(meta.page);
    }, [filtros, meta.page]);

    useEffect(() => {
        getFiltros(filtros.status || 'ativos')
            .then((data) => setOpcoesFiltro(data))
            .catch(() => {});
    }, [filtros.status]);

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
        const timeoutId = setTimeout(() => {
            void fetchDados();
        }, 280);
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
            [chave]: obterValorPadraoCampo(chave),
        }));
    };

    const mudarPagina = (novaPagina) => {
        setMeta((prev) => ({ ...prev, page: novaPagina }));
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const chipsAtivos = useMemo(() => construirChipsFiltrosAtivos(filtros), [filtros]);

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

    const sufixoModalidade = obterSufixoModalidadeTitulo(filtros.modalidade);

    return (
        <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex flex-col lg:flex-row gap-7 items-start">
                <Filtros
                    opcoes={opcoesFiltro}
                    filtros={filtros}
                    setFiltros={handleFiltrosChange}
                    onLimpar={limparFiltros}
                    abertoMobile={abertoMobile}
                    setAbertoMobile={setAbertoMobile}
                    totalResultados={meta.total}
                />

                <main className="flex-1 w-full min-w-0">
                    <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm mb-5">
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                            <div className="flex items-center justify-between sm:justify-start gap-3">
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
                                        {filtros.tipo || 'Imóveis'} {sufixoModalidade}
                                        {filtros.cidade ? ` em ${filtros.cidade}` : ''}
                                    </h2>
                                    <p className="text-xs text-gray-500">
                                        {loading
                                            ? 'Buscando imóveis...'
                                            : `${meta.total.toLocaleString('pt-BR')} imóvel(is) encontrado(s)`}
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center gap-2 self-end sm:self-auto">
                                <ArrowUpDown size={15} className="text-gray-400 shrink-0" />
                                <label
                                    htmlFor="seletor-ordenar-por"
                                    className="text-xs font-semibold text-gray-500 whitespace-nowrap"
                                >
                                    Ordenar por:
                                </label>
                                <select
                                    id="seletor-ordenar-por"
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

                    <GradeResultadosImoveis
                        loading={loading}
                        erro={erro}
                        imoveis={imoveis}
                        onLimparFiltros={limparFiltros}
                    />

                    {!loading && meta.pages > 1 && (
                        <div className="mt-10 flex flex-wrap justify-center items-center gap-2">
                            <button
                                type="button"
                                onClick={() => mudarPagina(meta.page - 1)}
                                disabled={meta.page === 1}
                                className="flex items-center gap-1 px-3.5 py-2 bg-white border border-gray-200 rounded-xl text-xs font-semibold text-gray-700 hover:bg-gray-50 disabled:opacity-40 disabled:pointer-events-none transition-colors"
                            >
                                <ChevronLeft size={15} /> Anterior
                            </button>

                            {paginasVisiveis[0] > 1 && (
                                <>
                                    <button
                                        type="button"
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
                                    type="button"
                                    key={num}
                                    onClick={() => mudarPagina(num)}
                                    className={`w-9 h-9 rounded-xl text-xs font-bold border transition-all ${
                                        meta.page === num
                                            ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
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
                                        type="button"
                                        onClick={() => mudarPagina(meta.pages)}
                                        className="w-9 h-9 rounded-xl text-xs font-semibold bg-white border border-gray-200 text-gray-700 hover:bg-gray-50"
                                    >
                                        {meta.pages}
                                    </button>
                                </>
                            )}

                            <button
                                type="button"
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