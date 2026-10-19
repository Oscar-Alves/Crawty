import { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import {
    Flame,
    Heart,
    X,
    SlidersHorizontal,
    MapPin,
    Bed,
    Bath,
    Car,
    Maximize,
    ExternalLink,
    ChevronLeft,
    ChevronRight,
    Trash2,
    Sparkles,
    RotateCcw,
    TrendingDown,
    Building2,
    Eye,
    CheckCircle2,
} from 'lucide-react';
import { getFiltros, getImoveis, getImovelDetalhes, registrarCliqueLead } from '../services/api';
import {
    lerIdsMatchesCookie,
    adicionarMatchCookie,
    removerMatchCookie,
    limparTodosMatchesCookie,
    obterImovelCacheMemoria,
    salvarImovelCacheMemoria,
} from '../utils/cookiesMatch';

const IMAGEM_PLACEHOLDER = 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=900&q=80';

const PREFERENCIAS_INICIAIS = {
    modalidade: 'VENDA',
    cidade: 'São João del Rei',
    bairro: '',
    tipo: '',
    preco_max: '',
    quartos_min: '',
    banheiros_min: '',
    vagas_min: '',
    ordenar_por: 'recente',
};

const FAIXAS_ORCAMENTO_VENDA = [
    { label: 'Sem limite', valor: '' },
    { label: 'Até R$ 300 mil', valor: '300000' },
    { label: 'Até R$ 500 mil', valor: '500000' },
    { label: 'Até R$ 800 mil', valor: '800000' },
    { label: 'Até R$ 1,2 mi', valor: '1200000' },
];

const FAIXAS_ORCAMENTO_ALUGUEL = [
    { label: 'Sem limite', valor: '' },
    { label: 'Até R$ 1.200', valor: '1200' },
    { label: 'Até R$ 2.000', valor: '2000' },
    { label: 'Até R$ 3.500', valor: '3500' },
    { label: 'Até R$ 5.000', valor: '5000' },
];

const OPCOES_QUARTOS = [
    { label: 'Qualquer', valor: '' },
    { label: '1+', valor: '1' },
    { label: '2+', valor: '2' },
    { label: '3+', valor: '3' },
    { label: '4+', valor: '4' },
];

const OPCOES_BANHEIROS = [
    { label: 'Qualquer', valor: '' },
    { label: '1+', valor: '1' },
    { label: '2+', valor: '2' },
    { label: '3+', valor: '3' },
];

const OPCOES_VAGAS = [
    { label: 'Qualquer', valor: '' },
    { label: '1+', valor: '1' },
    { label: '2+', valor: '2' },
];

const formatarMoeda = (valor) => {
    if (!valor || Number(valor) <= 0) return 'Sob Consulta';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        maximumFractionDigits: 0,
    }).format(valor);
};

const obterListaBairrosDaCidade = (opcoesBanco, cidadeSelecionada) => {
    if (!cidadeSelecionada) return opcoesBanco.bairros || [];
    const mapa = opcoesBanco.bairros_por_cidade || {};
    return mapa[cidadeSelecionada] || opcoesBanco.bairros || [];
};

const calcularPercentualQueda = (imovel) => {
    const atual = Number(imovel?.preco || 0);
    const anterior = Number(imovel?.preco_anterior || 0);
    if (anterior <= 0 || atual <= 0 || anterior <= atual) return 0;
    return Math.round(((anterior - atual) / anterior) * 100);
};

const obterAreaExibicao = (imovel) => {
    return imovel?.area_util || imovel?.area_total || imovel?.area_construida || 0;
};

const montarParametrosBuscaMatch = (preferencias, pagina) => ({
    page: pagina,
    limit: 24,
    status: 'ativos',
    apenas_com_foto: true,
    modalidade: preferencias.modalidade,
    cidade: preferencias.cidade,
    bairro: preferencias.bairro,
    tipo: preferencias.tipo,
    preco_max: preferencias.preco_max,
    quartos_min: preferencias.quartos_min,
    banheiros_min: preferencias.banheiros_min,
    vagas_min: preferencias.vagas_min,
    ordenar_por: preferencias.ordenar_por,
});

const BarraSuperiorMatch = ({
    etapa,
    totalMatches,
    onVoltarPreferencias,
    onAbrirGavetaMatches,
}) => (
    <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-rose-500 to-orange-500 flex items-center justify-center text-white shadow-md shadow-rose-200">
                <Flame size={24} />
            </div>
            <div>
                <div className="flex items-center gap-2">
                    <h1 className="text-xl sm:text-2xl font-extrabold text-gray-900 tracking-tight">
                        Modo Match
                    </h1>
                    <span className="text-[11px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-rose-100 text-rose-700">
                        Descubra seu Imóvel
                    </span>
                </div>
                <p className="text-xs sm:text-sm text-gray-500">
                    {etapa === 'preferencias'
                        ? 'Defina o perfil do imóvel ideal antes de começar a deslizar pelos cards'
                        : 'Avalie cada imóvel: dê Match para salvar nos seus favoritos ou passe para o próximo'}
                </p>
            </div>
        </div>

        <div className="flex items-center gap-2.5">
            {etapa === 'deck' && (
                <button
                    type="button"
                    onClick={onVoltarPreferencias}
                    className="inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl text-xs sm:text-sm font-semibold text-gray-700 bg-white border border-gray-200 hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm"
                >
                    <SlidersHorizontal size={16} className="text-gray-500" />
                    <span>Preferências</span>
                </button>
            )}

            <button
                type="button"
                onClick={onAbrirGavetaMatches}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold text-white bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-600 hover:to-pink-700 transition-all shadow-sm"
            >
                <Heart size={16} className="fill-white" />
                <span>Meus Matches</span>
                <span className="px-2 py-0.5 rounded-full text-xs font-extrabold bg-white/25 text-white">
                    {totalMatches}
                </span>
            </button>
        </div>
    </div>
);

const TelaPreferenciasMatch = ({
    preferencias,
    opcoesBanco,
    onAtualizarCampo,
    onIniciarDeck,
    onResetarPreferencias,
}) => {
    const bairrosDisponiveis = useMemo(
        () => obterListaBairrosDaCidade(opcoesBanco, preferencias.cidade),
        [opcoesBanco, preferencias.cidade]
    );

    const faixasOrcamento =
        preferencias.modalidade === 'ALUGUEL' ? FAIXAS_ORCAMENTO_ALUGUEL : FAIXAS_ORCAMENTO_VENDA;

    const tiposDisponiveis = opcoesBanco.tipos?.length
        ? opcoesBanco.tipos
        : ['Casa', 'Apartamento', 'Terreno', 'Comercial', 'Rural', 'Kitnet'];

    const selecionarModalidade = (novaModalidade) => {
        onAtualizarCampo('modalidade', novaModalidade);
        onAtualizarCampo('preco_max', '');
    };

    const selecionarCidade = (novaCidade) => {
        onAtualizarCampo('cidade', novaCidade);
        onAtualizarCampo('bairro', '');
    };

    return (
        <div className="max-w-3xl mx-auto bg-white rounded-3xl border border-gray-200/90 shadow-sm overflow-hidden">
            <div className="bg-gradient-to-r from-rose-500 via-pink-600 to-orange-500 px-6 py-6 text-white">
                <div className="flex items-center gap-2 text-rose-100 text-xs font-bold uppercase tracking-wider mb-1">
                    <Sparkles size={15} />
                    <span>Passo 1 de 2 • Configuração de Perfil</span>
                </div>
                <h2 className="text-xl sm:text-2xl font-extrabold">
                    O que você procura no seu próximo imóvel?
                </h2>
                <p className="text-rose-50 text-xs sm:text-sm mt-1">
                    Personalize seus filtros abaixo. Vamos montar uma fila exclusiva de imóveis com fotos que combinam com você.
                </p>
            </div>

            <div className="p-6 sm:p-8 space-y-6">
                {/* Finalidade */}
                <div>
                    <span className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-2.5">
                        1. Qual é o seu objetivo?
                    </span>
                    <div className="grid grid-cols-3 gap-2.5">
                        {[
                            { label: 'Comprar', valor: 'VENDA' },
                            { label: 'Alugar', valor: 'ALUGUEL' },
                            { label: 'Ambos', valor: '' },
                        ].map((item) => {
                            const ativo = preferencias.modalidade === item.valor;
                            const classeBotao = ativo
                                ? 'bg-rose-50 border-rose-500 text-rose-700 font-bold shadow-sm'
                                : 'bg-gray-50 border-gray-200 text-gray-700 hover:bg-gray-100 font-medium';
                            return (
                                <button
                                    key={item.label}
                                    type="button"
                                    onClick={() => selecionarModalidade(item.valor)}
                                    className={`py-3 px-4 rounded-2xl border text-sm transition-all ${classeBotao}`}
                                >
                                    {item.label}
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Localização */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                        <label
                            htmlFor="match-select-cidade"
                            className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-2"
                        >
                            2. Cidade
                        </label>
                        <select
                            id="match-select-cidade"
                            value={preferencias.cidade}
                            onChange={(e) => selecionarCidade(e.target.value)}
                            className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-sm text-gray-800 focus:bg-white focus:border-rose-500 focus:outline-none"
                        >
                            <option value="">Todas as cidades da região</option>
                            {(opcoesBanco.cidades || []).map((cid) => (
                                <option key={cid} value={cid}>
                                    {cid}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label
                            htmlFor="match-select-bairro"
                            className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-2"
                        >
                            Bairro de Preferência (Opcional)
                        </label>
                        <select
                            id="match-select-bairro"
                            value={preferencias.bairro}
                            onChange={(e) => onAtualizarCampo('bairro', e.target.value)}
                            className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-sm text-gray-800 focus:bg-white focus:border-rose-500 focus:outline-none"
                        >
                            <option value="">Todos os bairros</option>
                            {bairrosDisponiveis.map((b) => (
                                <option key={b} value={b}>
                                    {b}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Tipo de Imóvel */}
                <div>
                    <div className="flex items-center justify-between mb-2.5">
                        <span className="block text-xs font-bold uppercase tracking-wider text-gray-500">
                            3. Tipo de Imóvel (pode escolher mais de um)
                        </span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        <button
                            type="button"
                            onClick={() => onAtualizarCampo('tipo', '')}
                            className={`px-3.5 py-2 rounded-xl text-xs sm:text-sm border transition-all ${
                                preferencias.tipo === ''
                                    ? 'bg-gray-900 text-white border-gray-900 font-bold'
                                    : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 font-medium'
                            }`}
                        >
                            Todos os tipos
                        </button>
                        {tiposDisponiveis.map((tipoItem) => {
                            const listaTipos = String(preferencias.tipo || '')
                                .split(',')
                                .map((item) => item.trim())
                                .filter(Boolean);
                            const selecionado = listaTipos.includes(tipoItem);
                            const classeChip = selecionado
                                ? 'bg-rose-600 text-white border-rose-600 font-bold shadow-sm'
                                : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100 font-medium';
                            const alternarTipoMatch = () => {
                                const novaLista = selecionado
                                    ? listaTipos.filter((item) => item !== tipoItem)
                                    : [...listaTipos, tipoItem];
                                onAtualizarCampo('tipo', novaLista.join(','));
                            };
                            return (
                                <button
                                    key={tipoItem}
                                    type="button"
                                    onClick={alternarTipoMatch}
                                    className={`px-3.5 py-2 rounded-xl text-xs sm:text-sm border transition-all ${classeChip}`}
                                >
                                    {tipoItem}
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Orçamento Máximo */}
                <div>
                    <label
                        htmlFor="match-input-preco-max"
                        className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-2.5"
                    >
                        4. Orçamento Máximo (R$)
                    </label>
                    <div className="flex flex-wrap gap-2 mb-3">
                        {faixasOrcamento.map((faixa) => {
                            const ativo = String(preferencias.preco_max) === faixa.valor;
                            const classeFaixa = ativo
                                ? 'bg-rose-50 border-rose-500 text-rose-700 font-bold'
                                : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100 font-medium';
                            return (
                                <button
                                    key={faixa.label}
                                    type="button"
                                    onClick={() => onAtualizarCampo('preco_max', faixa.valor)}
                                    className={`px-3 py-1.5 rounded-xl text-xs border transition-all ${classeFaixa}`}
                                >
                                    {faixa.label}
                                </button>
                            );
                        })}
                    </div>
                    <input
                        id="match-input-preco-max"
                        type="number"
                        min="0"
                        step="1000"
                        placeholder="Ou digite um valor máximo personalizado (ex: 450000)"
                        value={preferencias.preco_max}
                        onChange={(e) => onAtualizarCampo('preco_max', e.target.value)}
                        className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-sm text-gray-800 focus:bg-white focus:border-rose-500 focus:outline-none"
                    />
                </div>

                {/* Quartos, Banheiros e Vagas */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                        <span className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
                            Quartos Mínimos
                        </span>
                        <div className="flex gap-1.5">
                            {OPCOES_QUARTOS.map((op) => {
                                const ativo = preferencias.quartos_min === op.valor;
                                return (
                                    <button
                                        key={op.label}
                                        type="button"
                                        onClick={() => onAtualizarCampo('quartos_min', op.valor)}
                                        className={`flex-1 py-2 rounded-xl text-xs border transition-all ${
                                            ativo
                                                ? 'bg-rose-600 text-white border-rose-600 font-bold'
                                                : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                                        }`}
                                    >
                                        {op.label}
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    <div>
                        <span className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
                            Banheiros Mínimos
                        </span>
                        <div className="flex gap-1.5">
                            {OPCOES_BANHEIROS.map((op) => {
                                const ativo = preferencias.banheiros_min === op.valor;
                                return (
                                    <button
                                        key={op.label}
                                        type="button"
                                        onClick={() => onAtualizarCampo('banheiros_min', op.valor)}
                                        className={`flex-1 py-2 rounded-xl text-xs border transition-all ${
                                            ativo
                                                ? 'bg-rose-600 text-white border-rose-600 font-bold'
                                                : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                                        }`}
                                    >
                                        {op.label}
                                    </button>
                                );
                            })}
                        </div>
                    </div>

                    <div>
                        <span className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-2">
                            Vagas de Garagem
                        </span>
                        <div className="flex gap-1.5">
                            {OPCOES_VAGAS.map((op) => {
                                const ativo = preferencias.vagas_min === op.valor;
                                return (
                                    <button
                                        key={op.label}
                                        type="button"
                                        onClick={() => onAtualizarCampo('vagas_min', op.valor)}
                                        className={`flex-1 py-2 rounded-xl text-xs border transition-all ${
                                            ativo
                                                ? 'bg-rose-600 text-white border-rose-600 font-bold'
                                                : 'bg-gray-50 text-gray-700 border-gray-200 hover:bg-gray-100'
                                        }`}
                                    >
                                        {op.label}
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* Ordenação */}
                <div>
                    <label
                        htmlFor="match-select-ordem"
                        className="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-2"
                    >
                        5. Ordem de apresentação dos cards
                    </label>
                    <select
                        id="match-select-ordem"
                        value={preferencias.ordenar_por}
                        onChange={(e) => onAtualizarCampo('ordenar_por', e.target.value)}
                        className="w-full sm:w-72 rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-sm text-gray-800 focus:bg-white focus:border-rose-500 focus:outline-none"
                    >
                        <option value="recente">Mais recentes primeiro</option>
                        <option value="preco_asc">Menor preço primeiro</option>
                        <option value="area_desc">Maior área útil primeiro</option>
                    </select>
                </div>

                {/* Botões de Ação */}
                <div className="pt-4 border-t border-gray-100 flex flex-col sm:flex-row items-center justify-between gap-3">
                    <button
                        type="button"
                        onClick={onResetarPreferencias}
                        className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-gray-800 transition-colors"
                    >
                        <RotateCcw size={14} />
                        <span>Restaurar padrões</span>
                    </button>

                    <button
                        type="button"
                        onClick={onIniciarDeck}
                        className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-8 py-3.5 rounded-2xl text-sm sm:text-base font-extrabold text-white bg-gradient-to-r from-rose-500 via-pink-600 to-orange-500 hover:from-rose-600 hover:via-pink-700 hover:to-orange-600 shadow-md shadow-rose-200 transition-all"
                    >
                        <Flame size={20} />
                        <span>Começar a Descobrir Imóveis</span>
                    </button>
                </div>
            </div>
        </div>
    );
};

const GaleriaCardMatch = ({ imovel, indiceFoto, onMudarFoto }) => {
    const fotos = imovel?.fotos?.length ? imovel.fotos : [IMAGEM_PLACEHOLDER];
    const totalFotos = fotos.length;
    const fotoAtual = fotos[indiceFoto] || IMAGEM_PLACEHOLDER;
    const percentualQueda = calcularPercentualQueda(imovel);

    const irFotoAnterior = (e) => {
        e.stopPropagation();
        onMudarFoto((indiceFoto - 1 + totalFotos) % totalFotos);
    };

    const irProximaFoto = (e) => {
        e.stopPropagation();
        onMudarFoto((indiceFoto + 1) % totalFotos);
    };

    return (
        <div className="relative h-72 sm:h-96 bg-gray-900 select-none overflow-hidden">
            <img
                src={fotoAtual}
                alt={imovel.titulo || 'Imóvel'}
                onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = IMAGEM_PLACEHOLDER;
                }}
                className="w-full h-full object-cover transition-all duration-300"
            />

            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-black/30 pointer-events-none" />

            {/* Indicadores de foto no topo */}
            {totalFotos > 1 && (
                <div className="absolute top-3 inset-x-4 flex gap-1.5 z-10">
                    {fotos.slice(0, 10).map((urlFoto, idx) => (
                        <div
                            key={`${imovel.id_unico}-bar-${urlFoto}`}
                            className={`h-1 flex-1 rounded-full transition-all ${
                                idx === indiceFoto ? 'bg-white' : 'bg-white/40'
                            }`}
                        />
                    ))}
                </div>
            )}

            {/* Badges superiores */}
            <div className="absolute top-6 left-4 right-4 flex items-center justify-between gap-2 z-10">
                <div className="flex flex-wrap items-center gap-1.5">
                    <span className="px-2.5 py-1 rounded-lg text-[11px] font-extrabold uppercase tracking-wider bg-blue-600 text-white shadow-sm">
                        {imovel.modalidade || 'VENDA'}
                    </span>
                    <span className="px-2.5 py-1 rounded-lg text-[11px] font-bold bg-black/60 text-white backdrop-blur-sm">
                        {imovel.subtipo && imovel.subtipo !== 'Padrão' ? imovel.subtipo : imovel.tipo || 'Imóvel'}
                    </span>
                    {percentualQueda > 0 && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-extrabold bg-emerald-500 text-white shadow-sm">
                            <TrendingDown size={12} />
                            <span>-{percentualQueda}%</span>
                        </span>
                    )}
                </div>

                <span className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-black/60 text-white backdrop-blur-sm">
                    {indiceFoto + 1} / {totalFotos}
                </span>
            </div>

            {/* Setas de navegação de fotos */}
            {totalFotos > 1 && (
                <>
                    <button
                        type="button"
                        onClick={irFotoAnterior}
                        aria-label="Foto anterior"
                        className="absolute left-3 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-black/50 hover:bg-black/75 text-white flex items-center justify-center backdrop-blur-sm transition-all z-10"
                    >
                        <ChevronLeft size={20} />
                    </button>
                    <button
                        type="button"
                        onClick={irProximaFoto}
                        aria-label="Próxima foto"
                        className="absolute right-3 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-black/50 hover:bg-black/75 text-white flex items-center justify-center backdrop-blur-sm transition-all z-10"
                    >
                        <ChevronRight size={20} />
                    </button>
                </>
            )}

            {/* Preço e localização sobrepostos na base da foto */}
            <div className="absolute bottom-4 left-5 right-5 text-white z-10">
                <div className="flex items-baseline justify-between gap-2">
                    <p className="text-2xl sm:text-3xl font-extrabold tracking-tight drop-shadow-sm">
                        {formatarMoeda(imovel.preco)}
                    </p>
                    <span className="inline-flex items-center gap-1 text-xs font-semibold text-gray-200 bg-white/15 px-2.5 py-1 rounded-lg backdrop-blur-sm">
                        <Building2 size={13} />
                        <span>{imovel.imobiliaria || 'Imobiliária'}</span>
                    </span>
                </div>
                <p className="text-sm sm:text-base font-bold text-gray-100 line-clamp-1 mt-1">
                    {imovel.titulo || `${imovel.tipo || 'Imóvel'} em ${imovel.bairro || imovel.cidade}`}
                </p>
                <p className="inline-flex items-center gap-1 text-xs text-gray-300 mt-0.5">
                    <MapPin size={13} className="text-rose-400 shrink-0" />
                    <span>
                        {imovel.bairro || 'Bairro não informado'} • {imovel.cidade || 'São João del Rei'}
                    </span>
                </p>
            </div>
        </div>
    );
};

const CardImovelMatch = ({
    imovel,
    animacaoSaida,
    onPassar,
    onDarMatch,
}) => {
    const [indiceFoto, setIndiceFoto] = useState(0);
    const areaExibicao = obterAreaExibicao(imovel);

    useEffect(() => {
        setIndiceFoto(0);
    }, [imovel?.id_unico]);

    let classeAnimacao = 'translate-x-0 rotate-0 opacity-100';
    if (animacaoSaida === 'esquerda') {
        classeAnimacao = '-translate-x-24 -rotate-6 opacity-0';
    } else if (animacaoSaida === 'direita') {
        classeAnimacao = 'translate-x-24 rotate-6 opacity-0';
    }

    return (
        <div
            className={`max-w-lg mx-auto bg-white rounded-3xl border border-gray-200/90 shadow-lg overflow-hidden transition-all duration-200 ${classeAnimacao}`}
        >
            <GaleriaCardMatch
                imovel={imovel}
                indiceFoto={indiceFoto}
                onMudarFoto={setIndiceFoto}
            />

            <div className="p-5 sm:p-6">
                {/* Atributos principais */}
                <div className="grid grid-cols-4 gap-2 pb-4 border-b border-gray-100 text-center">
                    <div className="bg-gray-50 rounded-2xl py-2.5 px-2">
                        <div className="flex items-center justify-center gap-1 text-gray-700 font-extrabold text-sm">
                            <Bed size={16} className="text-blue-600" />
                            <span>{imovel.quartos || 0}</span>
                        </div>
                        <span className="block text-[11px] text-gray-500 font-medium mt-0.5">
                            Quartos
                        </span>
                    </div>

                    <div className="bg-gray-50 rounded-2xl py-2.5 px-2">
                        <div className="flex items-center justify-center gap-1 text-gray-700 font-extrabold text-sm">
                            <Bath size={16} className="text-blue-600" />
                            <span>{imovel.banheiros || 0}</span>
                        </div>
                        <span className="block text-[11px] text-gray-500 font-medium mt-0.5">
                            Banheiros
                        </span>
                    </div>

                    <div className="bg-gray-50 rounded-2xl py-2.5 px-2">
                        <div className="flex items-center justify-center gap-1 text-gray-700 font-extrabold text-sm">
                            <Car size={16} className="text-blue-600" />
                            <span>{imovel.vagas || 0}</span>
                        </div>
                        <span className="block text-[11px] text-gray-500 font-medium mt-0.5">
                            Vagas
                        </span>
                    </div>

                    <div className="bg-gray-50 rounded-2xl py-2.5 px-2">
                        <div className="flex items-center justify-center gap-1 text-gray-700 font-extrabold text-sm">
                            <Maximize size={15} className="text-blue-600" />
                            <span>{areaExibicao > 0 ? `${areaExibicao}m²` : '--'}</span>
                        </div>
                        <span className="block text-[11px] text-gray-500 font-medium mt-0.5">
                            Área
                        </span>
                    </div>
                </div>

                {/* Descrição resumida */}
                {imovel.descricao && (
                    <p className="text-xs sm:text-sm text-gray-600 line-clamp-2 mt-4">
                        {imovel.descricao}
                    </p>
                )}

                {/* Botões estilo Tinder */}
                <div className="mt-6 flex items-center justify-center gap-4 sm:gap-6">
                    <button
                        type="button"
                        onClick={onPassar}
                        title="Passar para o próximo (Seta Esquerda)"
                        className="flex-1 inline-flex items-center justify-center gap-2 py-3.5 px-5 rounded-2xl border-2 border-gray-200 text-gray-700 hover:border-gray-400 hover:bg-gray-50 font-bold text-sm transition-all active:scale-95"
                    >
                        <X size={20} className="text-gray-500" />
                        <span>Passar</span>
                    </button>

                    <Link
                        to={`/imovel/${imovel.id_unico}`}
                        title="Ver ficha completa do imóvel"
                        className="w-12 h-12 rounded-2xl border border-gray-200 bg-gray-50 hover:bg-blue-50 hover:border-blue-200 text-gray-600 hover:text-blue-600 flex items-center justify-center transition-all shrink-0"
                    >
                        <Eye size={20} />
                    </Link>

                    <button
                        type="button"
                        onClick={onDarMatch}
                        title="Dar Match e salvar imóvel (Seta Direita)"
                        className="flex-1 inline-flex items-center justify-center gap-2 py-3.5 px-5 rounded-2xl bg-gradient-to-r from-rose-500 to-pink-600 hover:from-rose-600 hover:to-pink-700 text-white font-extrabold text-sm shadow-md shadow-rose-200 transition-all active:scale-95"
                    >
                        <Heart size={20} className="fill-white" />
                        <span>Match!</span>
                    </button>
                </div>

                <p className="text-center text-[11px] text-gray-400 mt-3">
                    Dica: no computador, use as setas <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600 font-semibold">←</kbd> para passar e <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-600 font-semibold">→</kbd> para dar Match
                </p>
            </div>
        </div>
    );
};

const GavetaMeusMatches = ({
    aberta,
    imoveisMatch,
    carregandoMatches,
    onFechar,
    onRemoverMatch,
    onLimparTodos,
}) => {
    if (!aberta) return null;

    const abrirSiteImobiliaria = (imovel) => {
        if (!imovel?.link) return;
        registrarCliqueLead(imovel.id_unico, 'match');
        globalThis.open(imovel.link, '_blank', 'noopener,noreferrer');
    };

    return (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/50 backdrop-blur-sm">
            <div className="w-full max-w-md bg-white h-full shadow-2xl flex flex-col">
                <div className="p-5 border-b border-gray-100 flex items-center justify-between bg-gradient-to-r from-rose-50 to-pink-50">
                    <div className="flex items-center gap-2.5">
                        <div className="w-9 h-9 rounded-xl bg-rose-500 text-white flex items-center justify-center">
                            <Heart size={18} className="fill-white" />
                        </div>
                        <div>
                            <h3 className="text-base font-extrabold text-gray-900">
                                Meus Matches ({imoveisMatch.length})
                            </h3>
                            <p className="text-xs text-gray-500">
                                Salvos nos cookies deste navegador
                            </p>
                        </div>
                    </div>

                    <button
                        type="button"
                        onClick={onFechar}
                        aria-label="Fechar lista de matches"
                        className="p-2 rounded-xl text-gray-500 hover:text-gray-800 hover:bg-white/80 transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {imoveisMatch.length > 0 && (
                    <div className="px-5 py-2.5 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
                        <span className="text-xs text-gray-500 font-medium">
                            Seus imóveis favoritos ficam disponíveis ao voltar ao site
                        </span>
                        <button
                            type="button"
                            onClick={onLimparTodos}
                            className="text-xs font-bold text-rose-600 hover:text-rose-700 hover:underline shrink-0 ml-2"
                        >
                            Limpar todos
                        </button>
                    </div>
                )}

                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    {carregandoMatches && imoveisMatch.length === 0 && (
                        <div className="py-12 text-center text-sm text-gray-500">
                            Carregando seus imóveis salvos...
                        </div>
                    )}

                    {!carregandoMatches && imoveisMatch.length === 0 && (
                        <div className="py-16 px-4 text-center">
                            <div className="w-14 h-14 rounded-2xl bg-rose-50 text-rose-400 flex items-center justify-center mx-auto mb-3">
                                <Heart size={28} />
                            </div>
                            <h4 className="text-base font-bold text-gray-800">
                                Nenhum Match salvo ainda
                            </h4>
                            <p className="text-xs text-gray-500 mt-1 max-w-xs mx-auto">
                                Quando você clicar em &ldquo;Match!&rdquo; em um imóvel, ele ficará salvo aqui para você visitar o site da imobiliária quando quiser.
                            </p>
                        </div>
                    )}

                    {imoveisMatch.map((imovel) => {
                        const fotoCapa = imovel.fotos?.[0] || IMAGEM_PLACEHOLDER;
                        return (
                            <div
                                key={imovel.id_unico}
                                className="flex gap-3 p-3 rounded-2xl border border-gray-200/90 hover:border-rose-200 bg-white shadow-sm transition-all"
                            >
                                <img
                                    src={fotoCapa}
                                    alt={imovel.titulo || 'Imóvel'}
                                    onError={(e) => {
                                        e.target.onerror = null;
                                        e.target.src = IMAGEM_PLACEHOLDER;
                                    }}
                                    className="w-24 h-24 rounded-xl object-cover shrink-0 bg-gray-100"
                                />

                                <div className="flex-1 min-w-0 flex flex-col justify-between">
                                    <div>
                                        <div className="flex items-start justify-between gap-2">
                                            <p className="text-sm font-extrabold text-gray-900 truncate">
                                                {formatarMoeda(imovel.preco)}
                                            </p>
                                            <button
                                                type="button"
                                                onClick={() => onRemoverMatch(imovel.id_unico)}
                                                title="Excluir este Match"
                                                className="p-1 rounded-lg text-gray-400 hover:text-rose-600 hover:bg-rose-50 transition-colors shrink-0"
                                            >
                                                <Trash2 size={15} />
                                            </button>
                                        </div>
                                        <p className="text-xs font-semibold text-gray-700 truncate">
                                            {imovel.titulo || `${imovel.tipo || 'Imóvel'} em ${imovel.bairro || imovel.cidade}`}
                                        </p>
                                        <p className="text-[11px] text-gray-500 truncate">
                                            {imovel.bairro || 'Bairro não inf.'} • {imovel.imobiliaria}
                                        </p>
                                    </div>

                                    <div className="flex items-center gap-2 mt-2">
                                        <button
                                            type="button"
                                            onClick={() => abrirSiteImobiliaria(imovel)}
                                            className="flex-1 inline-flex items-center justify-center gap-1 py-1.5 px-2.5 rounded-lg text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 transition-colors"
                                        >
                                            <span>Ir para Imobiliária</span>
                                            <ExternalLink size={12} />
                                        </button>
                                        <Link
                                            to={`/imovel/${imovel.id_unico}`}
                                            onClick={onFechar}
                                            className="py-1.5 px-2.5 rounded-lg text-xs font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
                                        >
                                            Detalhes
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};

const ModoMatch = () => {
    // Sempre inicia na tela de preferências ao entrar em /match
    const [etapa, setEtapa] = useState('preferencias');
    const [preferencias, setPreferencias] = useState(PREFERENCIAS_INICIAIS);
    const [opcoesBanco, setOpcoesBanco] = useState({
        cidades: [],
        bairros: [],
        bairros_por_cidade: {},
        tipos: [],
    });

    // Estado do Deck de Cards
    const [filaImoveis, setFilaImoveis] = useState([]);
    const [indiceAtual, setIndiceAtual] = useState(0);
    const [paginaDeck, setPaginaDeck] = useState(1);
    const [totalPaginasDeck, setTotalPaginasDeck] = useState(1);
    const [totalEncontrados, setTotalEncontrados] = useState(0);
    const [carregandoDeck, setCarregandoDeck] = useState(false);
    const [animacaoSaida, setAnimacaoSaida] = useState('');
    const [avisoMatchRecente, setAvisoMatchRecente] = useState('');

    // Estado dos Matches salvos no Cookie
    const [idsMatches, setIdsMatches] = useState(() => lerIdsMatchesCookie());
    const [imoveisMatch, setImoveisMatch] = useState([]);
    const [carregandoMatches, setCarregandoMatches] = useState(false);
    const [gavetaAberta, setGavetaAberta] = useState(false);

    // Carrega opções de cidades, bairros e tipos do backend
    useEffect(() => {
        getFiltros('ativos')
            .then((res) => {
                if (res?.cidades) {
                    setOpcoesBanco(res);
                }
            })
            .catch(() => {});
    }, []);

    // Hidrata os detalhes dos imóveis salvos no cookie
    useEffect(() => {
        let ativo = true;

        const carregarDetalhesMatches = async () => {
            if (idsMatches.length === 0) {
                setImoveisMatch([]);
                return;
            }

            setCarregandoMatches(true);
            const promessas = idsMatches.map(async (idUnico) => {
                const emCache = obterImovelCacheMemoria(idUnico);
                if (emCache) return emCache;
                try {
                    const dados = await getImovelDetalhes(idUnico);
                    if (dados?.id_unico) {
                        salvarImovelCacheMemoria(dados);
                        return dados;
                    }
                    return null;
                } catch {
                    return null;
                }
            });

            const resultados = await Promise.all(promessas);
            if (ativo) {
                setImoveisMatch(resultados.filter(Boolean));
                setCarregandoMatches(false);
            }
        };

        void carregarDetalhesMatches();
        return () => {
            ativo = false;
        };
    }, [idsMatches]);

    const buscarLoteImoveisDeck = useCallback(
        async (paginaSolicitada, anexar = false) => {
            setCarregandoDeck(true);
            try {
                const params = montarParametrosBuscaMatch(preferencias, paginaSolicitada);
                const resposta = await getImoveis(params);
                const novosItens = (resposta?.data || []).filter((item) => item?.id_unico);
                novosItens.forEach(salvarImovelCacheMemoria);

                setTotalPaginasDeck(resposta?.meta?.total_pages || 1);
                setTotalEncontrados(resposta?.meta?.total || novosItens.length);
                setPaginaDeck(paginaSolicitada);

                if (anexar) {
                    setFilaImoveis((prev) => [...prev, ...novosItens]);
                } else {
                    setFilaImoveis(novosItens);
                    setIndiceAtual(0);
                }
            } catch (error) {
                console.error('Erro ao buscar imóveis para o Modo Match:', error);
                if (!anexar) setFilaImoveis([]);
            } finally {
                setCarregandoDeck(false);
            }
        },
        [preferencias]
    );

    const handleAtualizarCampoPreferencia = (campo, valor) => {
        setPreferencias((prev) => ({ ...prev, [campo]: valor }));
    };

    const handleIniciarDeck = () => {
        setEtapa('deck');
        void buscarLoteImoveisDeck(1, false);
    };

    const imovelAtual = filaImoveis[indiceAtual] || null;

    const avancarParaProximoCard = useCallback(() => {
        const proximoIndice = indiceAtual + 1;
        setIndiceAtual(proximoIndice);
        setAnimacaoSaida('');

        const pertoDoFim = proximoIndice >= filaImoveis.length - 3;
        if (pertoDoFim && paginaDeck < totalPaginasDeck && !carregandoDeck) {
            void buscarLoteImoveisDeck(paginaDeck + 1, true);
        }
    }, [indiceAtual, filaImoveis.length, paginaDeck, totalPaginasDeck, carregandoDeck, buscarLoteImoveisDeck]);

    const handlePassarCard = useCallback(() => {
        if (!imovelAtual || animacaoSaida) return;
        setAnimacaoSaida('esquerda');
        setTimeout(() => {
            avancarParaProximoCard();
        }, 180);
    }, [imovelAtual, animacaoSaida, avancarParaProximoCard]);

    const handleDarMatchCard = useCallback(() => {
        if (!imovelAtual || animacaoSaida) return;
        const novosIds = adicionarMatchCookie(imovelAtual);
        setIdsMatches(novosIds);
        setAvisoMatchRecente(imovelAtual.titulo || 'Imóvel salvo nos seus Matches!');
        setAnimacaoSaida('direita');

        setTimeout(() => {
            avancarParaProximoCard();
        }, 180);

        setTimeout(() => {
            setAvisoMatchRecente('');
        }, 2400);
    }, [imovelAtual, animacaoSaida, avancarParaProximoCard]);

    // Atalhos de teclado (Setas Esquerda e Direita) quando estiver no Deck
    useEffect(() => {
        if (etapa !== 'deck' || gavetaAberta || !imovelAtual) return undefined;

        const aoPressionarTecla = (e) => {
            if (e.key === 'ArrowLeft') {
                e.preventDefault();
                handlePassarCard();
            } else if (e.key === 'ArrowRight') {
                e.preventDefault();
                handleDarMatchCard();
            }
        };

        globalThis.addEventListener('keydown', aoPressionarTecla);
        return () => globalThis.removeEventListener('keydown', aoPressionarTecla);
    }, [etapa, gavetaAberta, imovelAtual, handlePassarCard, handleDarMatchCard]);

    const handleRemoverMatch = (idUnico) => {
        const atualizados = removerMatchCookie(idUnico);
        setIdsMatches(atualizados);
    };

    const handleLimparTodosMatches = () => {
        const vazio = limparTodosMatchesCookie();
        setIdsMatches(vazio);
    };

    return (
        <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
            <BarraSuperiorMatch
                etapa={etapa}
                totalMatches={idsMatches.length}
                onVoltarPreferencias={() => setEtapa('preferencias')}
                onAbrirGavetaMatches={() => setGavetaAberta(true)}
            />

            {avisoMatchRecente && (
                <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 inline-flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-gray-900/95 text-white text-xs sm:text-sm font-bold shadow-xl">
                    <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
                    <span>Match salvo nos seus favoritos!</span>
                </div>
            )}

            {etapa === 'preferencias' && (
                <TelaPreferenciasMatch
                    preferencias={preferencias}
                    opcoesBanco={opcoesBanco}
                    onAtualizarCampo={handleAtualizarCampoPreferencia}
                    onIniciarDeck={handleIniciarDeck}
                    onResetarPreferencias={() => setPreferencias(PREFERENCIAS_INICIAIS)}
                />
            )}

            {etapa === 'deck' && (
                <div>
                    {/* Barra de progresso / resumo de filtros ativos */}
                    <div className="max-w-lg mx-auto mb-4 flex items-center justify-between text-xs text-gray-500 px-1">
                        <span>
                            {totalEncontrados > 0
                                ? `Imóvel ${Math.min(indiceAtual + 1, totalEncontrados)} de ${totalEncontrados} no seu perfil`
                                : 'Buscando imóveis compatíveis...'}
                        </span>
                        <button
                            type="button"
                            onClick={() => setEtapa('preferencias')}
                            className="font-semibold text-rose-600 hover:underline"
                        >
                            Alterar filtros
                        </button>
                    </div>

                    {carregandoDeck && filaImoveis.length === 0 && (
                        <div className="max-w-lg mx-auto bg-white rounded-3xl border border-gray-200 p-12 text-center shadow-sm">
                            <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-500 flex items-center justify-center mx-auto mb-3 animate-pulse">
                                <Flame size={24} />
                            </div>
                            <p className="text-base font-bold text-gray-800">
                                Preparando sua fila de imóveis...
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                                Selecionando os melhores anúncios com fotos de acordo com suas preferências.
                            </p>
                        </div>
                    )}

                    {!carregandoDeck && imovelAtual && (
                        <CardImovelMatch
                            imovel={imovelAtual}
                            animacaoSaida={animacaoSaida}
                            onPassar={handlePassarCard}
                            onDarMatch={handleDarMatchCard}
                        />
                    )}

                    {!carregandoDeck && !imovelAtual && (
                        <div className="max-w-lg mx-auto bg-white rounded-3xl border border-gray-200 p-10 text-center shadow-sm">
                            <div className="w-14 h-14 rounded-2xl bg-rose-50 text-rose-500 flex items-center justify-center mx-auto mb-4">
                                <Sparkles size={28} />
                            </div>
                            <h3 className="text-lg font-extrabold text-gray-900">
                                {filaImoveis.length === 0
                                    ? 'Nenhum imóvel encontrado com esses filtros'
                                    : 'Você chegou ao fim da fila!'}
                            </h3>
                            <p className="text-xs sm:text-sm text-gray-500 mt-1.5 max-w-sm mx-auto">
                                {filaImoveis.length === 0
                                    ? 'Tente flexibilizar o orçamento máximo ou selecionar todos os bairros para descobrir mais opções.'
                                    : 'Você avaliou todos os imóveis para esse perfil. Ajuste suas preferências ou confira seus Matches salvos!'}
                            </p>
                            <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
                                <button
                                    type="button"
                                    onClick={() => setEtapa('preferencias')}
                                    className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs sm:text-sm font-bold text-white bg-rose-600 hover:bg-rose-700 transition-colors"
                                >
                                    <SlidersHorizontal size={16} />
                                    <span>Ajustar Preferências</span>
                                </button>
                                {filaImoveis.length > 0 && (
                                    <button
                                        type="button"
                                        onClick={() => setIndiceAtual(0)}
                                        className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs sm:text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 transition-colors"
                                    >
                                        <RotateCcw size={16} />
                                        <span>Recomeçar Fila</span>
                                    </button>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            )}

            <GavetaMeusMatches
                aberta={gavetaAberta}
                imoveisMatch={imoveisMatch}
                carregandoMatches={carregandoMatches}
                onFechar={() => setGavetaAberta(false)}
                onRemoverMatch={handleRemoverMatch}
                onLimparTodos={handleLimparTodosMatches}
            />
        </main>
    );
};

export default ModoMatch;

