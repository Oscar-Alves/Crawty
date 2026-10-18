import { useState, useMemo } from 'react';
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
    status: 'ativos',
    ordenar_por: '',
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

const Filtros = ({ opcoes, filtros, setFiltros, onLimpar, abertoMobile, setAbertoMobile, totalResultados }) => {
    const [buscaBairro, setBuscaBairro] = useState('');

    // Lista de bairros filtrada pela cidade selecionada (ou todos se nenhuma cidade selecionada)
    const bairrosDisponiveis = useMemo(() => {
        const base =
            filtros.cidade && opcoes.bairros_por_cidade?.[filtros.cidade]
                ? opcoes.bairros_por_cidade[filtros.cidade]
                : opcoes.bairros || [];

        if (!buscaBairro.trim()) return base;
        const termo = buscaBairro.toLowerCase().trim();
        return base.filter((b) => b.toLowerCase().includes(termo));
    }, [filtros.cidade, opcoes.bairros, opcoes.bairros_por_cidade, buscaBairro]);

    // Lista de subtipos filtrada pelo tipo principal selecionado
    const subtiposDisponiveis = useMemo(() => {
        if (filtros.tipo && opcoes.subtipos_por_tipo?.[filtros.tipo]) {
            return opcoes.subtipos_por_tipo[filtros.tipo];
        }
        return opcoes.subtipos || [];
    }, [filtros.tipo, opcoes.subtipos, opcoes.subtipos_por_tipo]);

    const atualizarCampo = (campo, valor) => {
        setFiltros((prev) => {
            const novo = { ...prev, [campo]: valor };

            // Se mudou a cidade, verifica se o bairro atual pertence à nova cidade
            if (campo === 'cidade') {
                const bairrosDaNovaCidade = valor
                    ? opcoes.bairros_por_cidade?.[valor] || []
                    : opcoes.bairros || [];
                if (prev.bairro && !bairrosDaNovaCidade.includes(prev.bairro)) {
                    novo.bairro = '';
                }
            }

            // Se mudou o tipo, verifica se o subtipo atual pertence ao novo tipo
            if (campo === 'tipo') {
                const subtiposDoNovoTipo = valor
                    ? opcoes.subtipos_por_tipo?.[valor] || []
                    : opcoes.subtipos || [];
                if (prev.subtipo && !subtiposDoNovoTipo.includes(prev.subtipo)) {
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
        setFiltros((prev) => {
            const mesmaFaixa = String(prev.preco_min) === String(min) && String(prev.preco_max) === String(max);
            return {
                ...prev,
                preco_min: mesmaFaixa ? '' : min,
                preco_max: mesmaFaixa ? '' : max,
            };
        });
    };

    const qtdFiltrosAtivos = useMemo(() => {
        let count = 0;
        Object.entries(filtros).forEach(([k, v]) => {
            if (k === 'ordenar_por') return;
            if (k === 'status' && v === 'ativos') return;
            if (v !== '' && v !== false && v !== null && v !== undefined) count++;
        });
        return count;
    }, [filtros]);

    const inputClass =
        'w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-sm text-gray-800 placeholder-gray-400 focus:bg-white focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 outline-none transition-all';
    const sectionTitleClass =
        'flex items-center gap-1.5 text-xs font-bold text-gray-700 uppercase tracking-wider mb-2.5';

    const renderSeletorMinimo = (label, icone, campo, opcoesValores = [1, 2, 3, 4]) => {
        const valorAtual = String(filtros[campo] || '');
        return (
            <div>
                <label className="flex items-center gap-1.5 text-xs font-semibold text-gray-600 mb-1.5">
                    {icone}
                    {label}
                </label>
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
        filtros.modalidade === 'ALUGUEL' ? FAIXAS_PRECO_ALUGUEL : FAIXAS_PRECO_VENDA;

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
                            {qtdFiltrosAtivos > 0
                                ? `${qtdFiltrosAtivos} filtro(s) aplicado(s)`
                                : 'Refine sua busca'}
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    {qtdFiltrosAtivos > 0 && (
                        <button
                            type="button"
                            onClick={() => {
                                setBuscaBairro('');
                                onLimpar();
                            }}
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

            {/* 1. Finalidade (Comprar / Alugar) */}
            <div>
                <span className={sectionTitleClass}>Finalidade</span>
                <div className="grid grid-cols-3 gap-1.5 bg-gray-100 p-1 rounded-xl">
                    {[
                        { label: 'Todos', value: '' },
                        { label: 'Comprar', value: 'VENDA' },
                        { label: 'Alugar', value: 'ALUGUEL' },
                    ].map((opt) => {
                        const ativo = filtros.modalidade === opt.value;
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
                <label className={sectionTitleClass}>
                    <Search size={14} className="text-blue-600" />
                    Busca Rápida ou Código
                </label>
                <div className="relative">
                    <input
                        type="text"
                        name="busca"
                        value={filtros.busca}
                        onChange={handleInputChange}
                        placeholder="Ex: Cód. 1153, rua, condomínio..."
                        className={`${inputClass} pr-8`}
                    />
                    {filtros.busca && (
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
                    <label className="block text-xs font-medium text-gray-600 mb-1">Cidade</label>
                    <select
                        name="cidade"
                        value={filtros.cidade}
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
                        <label className="block text-xs font-medium text-gray-600">
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
                        name="bairro"
                        value={filtros.bairro}
                        onChange={handleInputChange}
                        className={inputClass}
                    >
                        <option value="">
                            {filtros.cidade
                                ? `Todos em ${filtros.cidade}`
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
                <span className={sectionTitleClass}>
                    <HomeIcon size={14} className="text-blue-600" />
                    Tipo de Imóvel
                </span>

                <div className="flex flex-wrap gap-1.5">
                    <button
                        type="button"
                        onClick={() => atualizarCampo('tipo', '')}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                            !filtros.tipo
                                ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                                : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                        }`}
                    >
                        Todos
                    </button>
                    {(opcoes.tipos || []).map((t) => {
                        const ativo = filtros.tipo === t;
                        return (
                            <button
                                key={t}
                                type="button"
                                onClick={() => atualizarCampo('tipo', ativo ? '' : t)}
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
                        <label className="block text-xs font-medium text-gray-600 mb-1">
                            Subtipo / Categoria Específica
                        </label>
                        <select
                            name="subtipo"
                            value={filtros.subtipo}
                            onChange={handleInputChange}
                            className={inputClass}
                        >
                            <option value="">
                                {filtros.tipo
                                    ? `Todos os subtipos de ${filtros.tipo}`
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
                        <label className="block text-[11px] font-medium text-gray-500 mb-1">
                            Mínimo (R$)
                        </label>
                        <input
                            type="number"
                            name="preco_min"
                            min="0"
                            step="500"
                            value={filtros.preco_min}
                            onChange={handleInputChange}
                            placeholder="R$ Mín"
                            className={inputClass}
                        />
                    </div>
                    <div>
                        <label className="block text-[11px] font-medium text-gray-500 mb-1">
                            Máximo (R$)
                        </label>
                        <input
                            type="number"
                            name="preco_max"
                            min="0"
                            step="500"
                            value={filtros.preco_max}
                            onChange={handleInputChange}
                            placeholder="R$ Máx"
                            className={inputClass}
                        />
                    </div>
                </div>

                {/* Sugestões rápidas de preço */}
                <div className="flex flex-wrap gap-1.5">
                    {faixasSugeridas.map((f, idx) => {
                        const selecionada =
                            String(filtros.preco_min) === f.min &&
                            String(filtros.preco_max) === f.max;
                        return (
                            <button
                                key={idx}
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
                        <label className="block text-[11px] font-medium text-gray-500 mb-1">
                            Mínima (m²)
                        </label>
                        <input
                            type="number"
                            name="area_min"
                            min="0"
                            value={filtros.area_min}
                            onChange={handleInputChange}
                            placeholder="Ex: 60"
                            className={inputClass}
                        />
                    </div>
                    <div>
                        <label className="block text-[11px] font-medium text-gray-500 mb-1">
                            Máxima (m²)
                        </label>
                        <input
                            type="number"
                            name="area_max"
                            min="0"
                            value={filtros.area_max}
                            onChange={handleInputChange}
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
                    <label className="block text-xs font-medium text-gray-600 mb-1">
                        Imobiliária
                    </label>
                    <select
                        name="imobiliaria"
                        value={filtros.imobiliaria}
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
                    <label className="flex items-center gap-1.5 text-xs font-medium text-gray-600 mb-1">
                        <Database size={13} className="text-gray-400" />
                        Disponibilidade do Anúncio
                    </label>
                    <select
                        name="status"
                        value={filtros.status || 'ativos'}
                        onChange={handleInputChange}
                        className={inputClass}
                    >
                        <option value="ativos">Apenas Anúncios Ativos</option>
                        <option value="descontinuados">Histórico (Retirados do Ar)</option>
                        <option value="todos">Todos (Ativos + Histórico)</option>
                    </select>
                </div>

                <label className="flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100/80 rounded-xl border border-gray-200 cursor-pointer transition-colors">
                    <span className="flex items-center gap-2 text-xs font-semibold text-gray-700">
                        <Camera size={15} className="text-blue-600" />
                        Apenas imóveis com fotos
                    </span>
                    <input
                        type="checkbox"
                        name="apenas_com_foto"
                        checked={Boolean(filtros.apenas_com_foto)}
                        onChange={handleInputChange}
                        className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                    />
                </label>
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
                    <div
                        className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
                        onClick={() => setAbertoMobile(false)}
                    />
                    <div className="relative ml-auto w-full max-w-sm bg-white h-full shadow-2xl flex flex-col z-10">
                        <div className="flex-1 overflow-y-auto p-5">{conteudoFiltros}</div>
                        <div className="p-4 border-t border-gray-100 bg-white">
                            <button
                                type="button"
                                onClick={() => setAbertoMobile(false)}
                                className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-md transition-colors text-sm"
                            >
                                Ver {totalResultados ?? ''} imóveis encontrados
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default Filtros;