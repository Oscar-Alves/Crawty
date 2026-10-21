import { useState, useMemo, useEffect } from 'react';
import {
    SlidersHorizontal,
    Search,
    MapPin,
    Building2,
    DollarSign,
    BedDouble,
    Sparkles,
    Bath,
    Car,
    Ruler,
    RotateCcw,
    X,
    Camera,
    Database,
    Home as HomeIcon,
    TrendingDown,
    Check,
} from 'lucide-react';

export const FILTROS_INICIAIS = {
    busca: '',
    modalidade: '',
    cidade: '',
    bairro: '',
    tipo: '',
    subtipo: '',
    imobiliaria: '',
    preco_min: '',
    preco_max: '',
    area_min: '',
    area_max: '',
    quartos_min: '',
    suites_min: '',
    banheiros_min: '',
    vagas_min: '',
    apenas_com_foto: false,
    apenas_queda_preco: false,
    status: 'ativos',
    ordenar_por: '',
};

const CHAVE_STORAGE_FILTROS = 'crawty_filtros_home';
const CHAVE_STORAGE_PAGINA = 'crawty_pagina_home';
const CHAVE_STORAGE_SCROLL = 'crawty_scroll_home';

let memoriaFiltros = { ...FILTROS_INICIAIS };
let memoriaPagina = 1;
let memoriaScroll = 0;

export const obterFiltrosSalvos = () => {
    try {
        const salvo = sessionStorage.getItem(CHAVE_STORAGE_FILTROS);
        if (salvo) {
            const parsed = JSON.parse(salvo);
            return { ...FILTROS_INICIAIS, ...parsed };
        }
    } catch {
        // fallback
    }
    return { ...FILTROS_INICIAIS, ...memoriaFiltros };
};

export const salvarFiltrosSalvos = (novosFiltros) => {
    const mesclado = { ...FILTROS_INICIAIS, ...novosFiltros };
    if (mesclado.ordenar_por === 'recentes') {
        mesclado.ordenar_por = 'recente';
    }
    memoriaFiltros = mesclado;
    try {
        sessionStorage.setItem(CHAVE_STORAGE_FILTROS, JSON.stringify(mesclado));
    } catch {
        // fallback
    }
};

export const obterPaginaSalva = () => {
    try {
        const salvo = sessionStorage.getItem(CHAVE_STORAGE_PAGINA);
        if (salvo) {
            const num = Number.parseInt(salvo, 10);
            if (!Number.isNaN(num) && num >= 1) return num;
        }
    } catch {
        // fallback
    }
    return memoriaPagina;
};

export const salvarPaginaSalva = (pagina) => {
    const num = Number.parseInt(String(pagina), 10);
    const valida = Number.isNaN(num) || num < 1 ? 1 : num;
    memoriaPagina = valida;
    try {
        sessionStorage.setItem(CHAVE_STORAGE_PAGINA, String(valida));
    } catch {
        // fallback
    }
};

export const obterScrollSalvo = () => {
    try {
        const salvo = sessionStorage.getItem(CHAVE_STORAGE_SCROLL);
        if (salvo) {
            const num = Number.parseInt(salvo, 10);
            if (!Number.isNaN(num) && num >= 0) return num;
        }
    } catch {
        // fallback
    }
    return memoriaScroll;
};

export const salvarScrollSalvo = (pos) => {
    const num = Number.parseInt(String(pos), 10);
    const valida = Number.isNaN(num) || num < 0 ? 0 : num;
    memoriaScroll = valida;
    try {
        sessionStorage.setItem(CHAVE_STORAGE_SCROLL, String(valida));
    } catch {
        // fallback
    }
};

const FAIXAS_PRECO_VENDA = [
    { label: 'Até 250 mil', min: '', max: '250000' },
    { label: '250 a 500 mil', min: '250000', max: '500000' },
    { label: '500 mil a 1M', min: '500000', max: '1000000' },
    { label: '+ de 1 milhão', min: '1000000', max: '' },
];

const FAIXAS_PRECO_ALUGUEL = [
    { label: 'Até R$ 1.200', min: '', max: '1200' },
    { label: 'R$ 1.200 a 2.500', min: '1200', max: '2500' },
    { label: 'R$ 2.500 a 5.000', min: '2500', max: '5000' },
    { label: '+ de R$ 5.000', min: '5000', max: '' },
];

const extrairListaTipos = (valorTipo) =>
    String(valorTipo || '')
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean);

const alternarTipoNaString = (valorAtual, tipoClicado) => {
    const lista = extrairListaTipos(valorAtual);
    if (lista.includes(tipoClicado)) {
        return lista.filter((item) => item !== tipoClicado).join(',');
    }
    return [...lista, tipoClicado].join(',');
};

const obterSubtiposDosTipos = (valorTipo, opcoes) => {
    const lista = extrairListaTipos(valorTipo);
    if (lista.length === 0) return opcoes.subtipos || [];
    const conjunto = new Set();
    for (const t of lista) {
        const subtipos = opcoes.subtipos_por_tipo?.[t] || [];
        for (const st of subtipos) {
            conjunto.add(st);
        }
    }
    return Array.from(conjunto).sort((a, b) => a.localeCompare(b));
};

const Filtros = ({
    opcoes,
    filtros,
    setFiltros,
    onAplicar,
    onLimpar,
    abertoMobile,
    setAbertoMobile,
    totalResultados,
}) => {
    // Mantém estado de rascunho local para que alterações não disparem requisições imediatas
    const [rascunho, setRascunho] = useState(() => ({ ...filtros }));
    const [buscaBairro, setBuscaBairro] = useState('');

    // Sincroniza rascunho sempre que os filtros aplicados mudarem externamente (ex: remoção de chips ou limpar)
    useEffect(() => {
        setRascunho({ ...filtros });
    }, [filtros]);

    // Lista de bairros filtrada pela cidade selecionada (ou todos se nenhuma cidade selecionada)
    const bairrosDisponiveis = useMemo(() => {
        const base =
            rascunho.cidade && opcoes.bairros_por_cidade?.[rascunho.cidade]
                ? opcoes.bairros_por_cidade[rascunho.cidade]
                : opcoes.bairros || [];

        if (!buscaBairro.trim()) return base;
        const termo = buscaBairro.toLowerCase().trim();
        return base.filter((b) => b.toLowerCase().includes(termo));
    }, [rascunho.cidade, opcoes.bairros, opcoes.bairros_por_cidade, buscaBairro]);

    const tiposSelecionados = useMemo(() => extrairListaTipos(rascunho.tipo), [rascunho.tipo]);

    // Lista de subtipos filtrada pelos tipos selecionados
    const subtiposDisponiveis = useMemo(
        () => obterSubtiposDosTipos(rascunho.tipo, opcoes),
        [rascunho.tipo, opcoes]
    );

    const atualizarCampo = (campo, valor) => {
        setRascunho((prev) => {
            const novo = { ...prev, [campo]: valor };

            if (campo === 'cidade') {
                const bairrosDaNovaCidade = valor
                    ? opcoes.bairros_por_cidade?.[valor] || []
                    : opcoes.bairros || [];
                if (prev.bairro && !bairrosDaNovaCidade.includes(prev.bairro)) {
                    novo.bairro = '';
                }
            }

            if (campo === 'tipo') {
                const subtiposValidos = obterSubtiposDosTipos(valor, opcoes);
                if (prev.subtipo && !subtiposValidos.includes(prev.subtipo)) {
                    novo.subtipo = '';
                }
            }

            return novo;
        });
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        atualizarCampo(name, type === 'checkbox' ? checked : value);
    };

    const aplicarFaixaPreco = (min, max) => {
        setRascunho((prev) => {
            const mesmaFaixa = String(prev.preco_min) === String(min) && String(prev.preco_max) === String(max);
            return {
                ...prev,
                preco_min: mesmaFaixa ? '' : min,
                preco_max: mesmaFaixa ? '' : max,
            };
        });
    };

    const qtdFiltrosAtivosRascunho = useMemo(() => {
        let count = 0;
        Object.entries(rascunho).forEach(([k, v]) => {
            if (k === 'ordenar_por') return;
            if (k === 'status' && v === 'ativos') return;
            if (v !== '' && v !== false && v !== null && v !== undefined) count++;
        });
        return count;
    }, [rascunho]);

    const temAlteracoesPendentes = useMemo(() => {
        const chaves = Object.keys(FILTROS_INICIAIS).filter((k) => k !== 'ordenar_por');
        return chaves.some((k) => String(rascunho[k] ?? '') !== String(filtros[k] ?? ''));
    }, [rascunho, filtros]);

    const handleAplicar = () => {
        if (typeof onAplicar === 'function') {
            onAplicar(rascunho);
        } else if (typeof setFiltros === 'function') {
            setFiltros(rascunho);
        }
        if (abertoMobile && typeof setAbertoMobile === 'function') {
            setAbertoMobile(false);
        }
    };

    const handleLimpar = () => {
        setBuscaBairro('');
        const resetado = { ...FILTROS_INICIAIS, ordenar_por: filtros.ordenar_por };
        setRascunho(resetado);
        if (typeof onLimpar === 'function') {
            onLimpar();
        } else if (typeof setFiltros === 'function') {
            setFiltros(resetado);
        }
        if (abertoMobile && typeof setAbertoMobile === 'function') {
            setAbertoMobile(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleAplicar();
        }
    };

    const inputClass =
        'w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 outline-none transition-all';
    const sectionTitleClass =
        'flex items-center gap-1.5 text-xs font-bold text-gray-700 uppercase tracking-wider mb-2.5';

    const renderSeletorMinimo = (label, icone, campo, opcoesValores = [1, 2, 3, 4]) => {
        const valorAtual = String(rascunho[campo] || '');
        return (
            <div>
                <span className="flex items-center gap-1.5 text-xs font-semibold text-gray-600 mb-1.5">
                    {icone}
                    {label}
                </span>
                <div className="grid grid-cols-5 gap-1.5">
                    <button
                        type="button"
                        onClick={() => atualizarCampo(campo, '')}
                        className={`py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                            valorAtual === ''
                                ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                                : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'
                        }`}
                    >
                        Todos
                    </button>
                    {opcoesValores.map((num) => {
                        const ativo = valorAtual === String(num);
                        return (
                            <button
                                key={num}
                                type="button"
                                onClick={() => atualizarCampo(campo, ativo ? '' : String(num))}
                                className={`py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                                    ativo
                                        ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                                        : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                                }`}
                            >
                                {num}+
                            </button>
                        );
                    })}
                </div>
            </div>
        );
    };

    const faixasSugeridas =
        rascunho.modalidade === 'ALUGUEL' ? FAIXAS_PRECO_ALUGUEL : FAIXAS_PRECO_VENDA;

    const conteudoFiltros = (
        <div className="space-y-6">
            {/* Cabeçalho do Painel */}
            <div className="flex items-center justify-between pb-4 border-b border-gray-100">
                <div className="flex items-center gap-2">
                    <div className="p-2 bg-blue-50 text-blue-600 rounded-xl">
                        <SlidersHorizontal size={18} />
                    </div>
                    <div>
                        <h2 className="font-bold text-gray-900 text-base leading-tight">Filtros</h2>
                        <p className="text-xs text-gray-500">
                            {qtdFiltrosAtivosRascunho > 0
                                ? `${qtdFiltrosAtivosRascunho} filtro(s) selecionado(s)`
                                : 'Refine sua busca'}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {qtdFiltrosAtivosRascunho > 0 && (
                        <button
                            type="button"
                            onClick={handleLimpar}
                            className="flex items-center gap-1 text-xs font-semibold text-red-600 hover:text-red-700 bg-red-50 hover:bg-red-100 px-2.5 py-1.5 rounded-lg transition-colors"
                        >
                            <RotateCcw size={13} />
                            Limpar
                        </button>
                    )}
                    {abertoMobile && (
                        <button
                            type="button"
                            onClick={() => setAbertoMobile(false)}
                            className="lg:hidden p-1.5 text-gray-400 hover:text-gray-700 rounded-lg"
                        >
                            <X size={20} />
                        </button>
                    )}
                </div>
            </div>

            {/* Botão de Aplicar no Topo da Sidebar (Desktop) */}
            <div className="hidden lg:block">
                <button
                    type="button"
                    onClick={handleAplicar}
                    className={`w-full py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all shadow-sm ${
                        temAlteracoesPendentes
                            ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-blue-500/25 ring-2 ring-blue-500/30'
                            : 'bg-blue-600 hover:bg-blue-700 text-white'
                    }`}
                >
                    <Check size={16} />
                    {temAlteracoesPendentes ? 'Aplicar Alterações' : 'Aplicar Filtros'}
                </button>
            </div>

            {/* 1. Finalidade (Comprar / Alugar) */}
            <div>
                <span className={sectionTitleClass}>Finalidade</span>
                <div className="grid grid-cols-3 gap-1.5 bg-gray-100 p-1 rounded-xl">
                    {[
                        { label: 'Todos', value: '' },
                        { label: 'Comprar', value: 'VENDA' },
                        { label: 'Alugar', value: 'ALUGUEL' },
                    ].map((opt) => {
                        const ativo = rascunho.modalidade === opt.value;
                        return (
                            <button
                                key={opt.value}
                                type="button"
                                onClick={() => atualizarCampo('modalidade', opt.value)}
                                className={`py-2 rounded-lg text-xs font-bold transition-all ${
                                    ativo
                                        ? 'bg-white text-blue-600 shadow-sm'
                                        : 'text-gray-600 hover:text-gray-900'
                                }`}
                            >
                                {opt.label}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* 2. Busca por Código, Rua ou Palavra-chave */}
            <div>
                <label htmlFor="filtro-busca" className={sectionTitleClass}>
                    <Search size={14} className="text-blue-600" />
                    Busca Rápida ou Código
                </label>
                <div className="relative">
                    <input
                        id="filtro-busca"
                        type="text"
                        name="busca"
                        value={rascunho.busca}
                        onChange={handleInputChange}
                        onKeyDown={handleKeyDown}
                        placeholder="Ex: Cód. 1153, rua, condomínio..."
                        className={`${inputClass} pr-8`}
                    />
                    {rascunho.busca && (
                        <button
                            type="button"
                            onClick={() => atualizarCampo('busca', '')}
                            className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                        >
                            <X size={15} />
                        </button>
                    )}
                </div>
            </div>

            {/* 3. Localização (Cidade & Bairro com busca) */}
            <div className="space-y-3 pt-2 border-t border-gray-100">
                <span className={sectionTitleClass}>
                    <MapPin size={14} className="text-blue-600" />
                    Localização
                </span>

                <div>
                    <label htmlFor="filtro-cidade" className="block text-xs font-medium text-gray-600 mb-1">
                        Cidade
                    </label>
                    <select
                        id="filtro-cidade"
                        name="cidade"
                        value={rascunho.cidade}
                        onChange={handleInputChange}
                        className={inputClass}
                    >
                        <option value="">Todas as Cidades ({opcoes.cidades?.length || 0})</option>
                        {(opcoes.cidades || []).map((c) => (
                            <option key={c} value={c}>
                                {c}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <div className="flex items-center justify-between mb-1">
                        <label htmlFor="filtro-bairro" className="block text-xs font-medium text-gray-600">
                            Bairro / Loteamento
                        </label>
                        <span className="text-[11px] text-gray-400">
                            {bairrosDisponiveis.length} opções
                        </span>
                    </div>

                    {/* Filtro rápido de bairros caso a lista seja grande */}
                    <div className="relative mb-1.5">
                        <input
                            type="text"
                            aria-label="Filtrar nome do bairro"
                            value={buscaBairro}
                            onChange={(e) => setBuscaBairro(e.target.value)}
                            placeholder="Filtrar nome do bairro..."
                            className="w-full px-2.5 py-1.5 bg-gray-50/70 border border-gray-200 rounded-lg text-xs text-gray-700 placeholder-gray-400 focus:bg-white focus:border-blue-500 outline-none"
                        />
                        {buscaBairro && (
                            <button
                                type="button"
                                onClick={() => setBuscaBairro('')}
                                className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                            >
                                <X size={13} />
                            </button>
                        )}
                    </div>

                    <select
                        id="filtro-bairro"
                        name="bairro"
                        value={rascunho.bairro}
                        onChange={handleInputChange}
                        className={inputClass}
                    >
                        <option value="">
                            {rascunho.cidade
                                ? `Todos em ${rascunho.cidade}`
                                : 'Todos os Bairros'}
                        </option>
                        {bairrosDisponiveis.map((b) => (
                            <option key={b} value={b}>
                                {b}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {/* 4. Tipo e Subtipo de Imóvel */}
            <div className="space-y-3 pt-2 border-t border-gray-100">
                <div className="flex items-center justify-between">
                    <span className="flex items-center gap-1.5 text-xs font-bold text-gray-700 uppercase tracking-wider">
                        <HomeIcon size={14} className="text-blue-600" />
                        Tipo de Imóvel
                    </span>
                    <span className="text-[11px] text-gray-400">Múltipla escolha</span>
                </div>

                <div className="flex flex-wrap gap-1.5">
                    <button
                        type="button"
                        onClick={() => atualizarCampo('tipo', '')}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                            tiposSelecionados.length === 0
                                ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                                : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                        }`}
                    >
                        Todos
                    </button>
                    {(opcoes.tipos || []).map((t) => {
                        const ativo = tiposSelecionados.includes(t);
                        return (
                            <button
                                key={t}
                                type="button"
                                onClick={() =>
                                    atualizarCampo('tipo', alternarTipoNaString(rascunho.tipo, t))
                                }
                                className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                                    ativo
                                        ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                                        : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                                }`}
                            >
                                {t}
                            </button>
                        );
                    })}
                </div>

                {subtiposDisponiveis.length > 0 && (
                    <div>
                        <label htmlFor="filtro-subtipo" className="block text-xs font-medium text-gray-600 mb-1">
                            Subtipo / Categoria Específica
                        </label>
                        <select
                            id="filtro-subtipo"
                            name="subtipo"
                            value={rascunho.subtipo}
                            onChange={handleInputChange}
                            className={inputClass}
                        >
                            <option value="">
                                {tiposSelecionados.length > 0
                                    ? `Todos os subtipos (${tiposSelecionados.join(' + ')})`
                                    : 'Todos os Subtipos'}
                            </option>
                            {subtiposDisponiveis.map((st) => (
                                <option key={st} value={st}>
                                    {st}
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </div>

            {/* 5. Faixa de Preço */}
            <div className="space-y-3 pt-2 border-t border-gray-100">
                <span className={sectionTitleClass}>
                    <DollarSign size={14} className="text-blue-600" />
                    Faixa de Preço (R$)
                </span>

                <div className="grid grid-cols-2 gap-2">
                    <div>
                        <label htmlFor="filtro-preco-min" className="block text-[11px] font-medium text-gray-500 mb-1">
                            Mínimo (R$)
                        </label>
                        <input
                            id="filtro-preco-min"
                            type="number"
                            name="preco_min"
                            min="0"
                            step="500"
                            value={rascunho.preco_min}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            placeholder="R$ Mín"
                            className={inputClass}
                        />
                    </div>
                    <div>
                        <label htmlFor="filtro-preco-max" className="block text-[11px] font-medium text-gray-500 mb-1">
                            Máximo (R$)
                        </label>
                        <input
                            id="filtro-preco-max"
                            type="number"
                            name="preco_max"
                            min="0"
                            step="500"
                            value={rascunho.preco_max}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            placeholder="R$ Máx"
                            className={inputClass}
                        />
                    </div>
                </div>

                {/* Sugestões rápidas de preço */}
                <div className="flex flex-wrap gap-1.5">
                    {faixasSugeridas.map((f) => {
                        const selecionada =
                            String(rascunho.preco_min) === f.min &&
                            String(rascunho.preco_max) === f.max;
                        return (
                            <button
                                key={f.label}
                                type="button"
                                onClick={() => aplicarFaixaPreco(f.min, f.max)}
                                className={`px-2.5 py-1 rounded-md text-[11px] font-medium border transition-colors ${
                                    selecionada
                                        ? 'bg-blue-50 text-blue-700 border-blue-300 font-semibold'
                                        : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'
                                }`}
                            >
                                {f.label}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* 6. Características (Quartos, Suítes, Banheiros, Vagas) */}
            <div className="space-y-3.5 pt-2 border-t border-gray-100">
                <span className={sectionTitleClass}>Características do Imóvel</span>

                {renderSeletorMinimo(
                    'Quartos',
                    <BedDouble size={14} className="text-blue-600" />,
                    'quartos_min',
                    [1, 2, 3, 4]
                )}

                {renderSeletorMinimo(
                    'Suítes',
                    <Sparkles size={14} className="text-blue-600" />,
                    'suites_min',
                    [1, 2, 3, 4]
                )}

                {renderSeletorMinimo(
                    'Banheiros',
                    <Bath size={14} className="text-blue-600" />,
                    'banheiros_min',
                    [1, 2, 3, 4]
                )}

                {renderSeletorMinimo(
                    'Vagas de Garagem',
                    <Car size={14} className="text-blue-600" />,
                    'vagas_min',
                    [1, 2, 3, 4]
                )}
            </div>

            {/* 7. Área (m²) */}
            <div className="space-y-2.5 pt-2 border-t border-gray-100">
                <span className={sectionTitleClass}>
                    <Ruler size={14} className="text-blue-600" />
                    Área (m²)
                </span>
                <div className="grid grid-cols-2 gap-2">
                    <div>
                        <label htmlFor="filtro-area-min" className="block text-[11px] font-medium text-gray-500 mb-1">
                            Mínima (m²)
                        </label>
                        <input
                            id="filtro-area-min"
                            type="number"
                            name="area_min"
                            min="0"
                            value={rascunho.area_min}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            placeholder="Ex: 60"
                            className={inputClass}
                        />
                    </div>
                    <div>
                        <label htmlFor="filtro-area-max" className="block text-[11px] font-medium text-gray-500 mb-1">
                            Máxima (m²)
                        </label>
                        <input
                            id="filtro-area-max"
                            type="number"
                            name="area_max"
                            min="0"
                            value={rascunho.area_max}
                            onChange={handleInputChange}
                            onKeyDown={handleKeyDown}
                            placeholder="Ex: 300"
                            className={inputClass}
                        />
                    </div>
                </div>
            </div>

            {/* 8. Imobiliária & Opções Extras */}
            <div className="space-y-3 pt-2 border-t border-gray-100">
                <span className={sectionTitleClass}>
                    <Building2 size={14} className="text-blue-600" />
                    Fonte & Preferências
                </span>

                <div>
                    <label htmlFor="filtro-imobiliaria" className="block text-xs font-medium text-gray-600 mb-1">
                        Imobiliária
                    </label>
                    <select
                        id="filtro-imobiliaria"
                        name="imobiliaria"
                        value={rascunho.imobiliaria}
                        onChange={handleInputChange}
                        className={inputClass}
                    >
                        <option value="">
                            Todas as Imobiliárias ({opcoes.imobiliarias?.length || 0})
                        </option>
                        {(opcoes.imobiliarias || []).map((imo) => (
                            <option key={imo} value={imo}>
                                {imo}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label htmlFor="filtro-status" className="flex items-center gap-1.5 text-xs font-medium text-gray-600 mb-1">
                        <Database size={13} className="text-gray-400" />
                        Disponibilidade do Anúncio
                    </label>
                    <select
                        id="filtro-status"
                        name="status"
                        value={rascunho.status || 'ativos'}
                        onChange={handleInputChange}
                        className={inputClass}
                    >
                        <option value="ativos">Apenas Anúncios Ativos</option>
                        <option value="descontinuados">Histórico (Retirados do Ar)</option>
                        <option value="todos">Todos (Ativos + Histórico)</option>
                    </select>
                </div>

                <label htmlFor="filtro-apenas-com-foto" className="flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100/80 rounded-xl border border-gray-200 cursor-pointer transition-colors">
                    <span className="flex items-center gap-2 text-xs font-semibold text-gray-700">
                        <Camera size={15} className="text-blue-600" />
                        Apenas imóveis com fotos
                    </span>
                    <input
                        id="filtro-apenas-com-foto"
                        type="checkbox"
                        name="apenas_com_foto"
                        checked={Boolean(rascunho.apenas_com_foto)}
                        onChange={handleInputChange}
                        className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                </label>

                <label htmlFor="filtro-apenas-queda-preco" className="flex items-center justify-between p-3 bg-rose-50/60 hover:bg-rose-50 rounded-xl border border-rose-200/70 cursor-pointer transition-colors">
                    <span className="flex items-center gap-2 text-xs font-semibold text-rose-800">
                        <TrendingDown size={15} className="text-rose-600" />
                        Apenas com redução de preço
                    </span>
                    <input
                        id="filtro-apenas-queda-preco"
                        type="checkbox"
                        name="apenas_queda_preco"
                        checked={Boolean(rascunho.apenas_queda_preco)}
                        onChange={handleInputChange}
                        className="w-4 h-4 text-rose-600 rounded border-gray-300 focus:ring-rose-500"
                    />
                </label>
            </div>

            {/* Botão de Aplicar no Rodapé da Sidebar (Desktop) */}
            <div className="hidden lg:block pt-2">
                <button
                    type="button"
                    onClick={handleAplicar}
                    className="w-full py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white shadow-md transition-colors"
                >
                    <Check size={16} />
                    Aplicar Filtros
                </button>
            </div>
        </div>
    );

    return (
        <>
            {/* Sidebar Desktop */}
            <aside className="hidden lg:block w-80 flex-shrink-0">
                <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 sticky top-20 max-h-[calc(100vh-6rem)] overflow-y-auto custom-scrollbar">
                    {conteudoFiltros}
                </div>
            </aside>

            {/* Drawer Mobile */}
            {abertoMobile && (
                <div className="fixed inset-0 z-50 lg:hidden flex">
                    <button
                        type="button"
                        aria-label="Fechar painel de filtros"
                        className="fixed inset-0 w-full h-full bg-black/50 backdrop-blur-sm transition-opacity border-0 cursor-default"
                        onClick={() => setAbertoMobile(false)}
                    />
                    <div className="relative ml-auto w-full max-w-sm bg-white h-full shadow-2xl flex flex-col z-10">
                        <div className="flex-1 overflow-y-auto p-5">{conteudoFiltros}</div>
                        <div className="p-4 border-t border-gray-100 bg-white flex gap-2">
                            <button
                                type="button"
                                onClick={handleLimpar}
                                className="py-3 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 font-bold rounded-xl transition-colors text-sm"
                            >
                                Limpar
                            </button>
                            <button
                                type="button"
                                onClick={handleAplicar}
                                className="flex-1 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-md transition-colors text-sm flex items-center justify-center gap-2"
                            >
                                <Check size={18} />
                                Aplicar Filtros
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default Filtros;
