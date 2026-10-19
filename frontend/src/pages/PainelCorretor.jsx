import { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
    Building2,
    BarChart3,
    LogOut,
    Phone,
    Mail,
    Globe,
    Award,
    Sparkles,
    MousePointerClick,
    Home,
    Lock,
    CheckCircle2,
    AlertCircle,
    Save,
    ArrowUpRight,
    Plus,
    Pencil,
    Trash2,
    Power,
    Eye,
    Search,
    TrendingDown,
    UserCog,
} from 'lucide-react';
import {
    obterMeuPerfilCorretorApi,
    atualizarPerfilCorretorApi,
    listarMeusImoveisCorretorApi,
    cadastrarImovelCorretorApi,
    editarImovelCorretorApi,
    alterarStatusImovelCorretorApi,
    excluirImovelCorretorApi,
} from '../services/api';
import {
    estaAutenticadoCorretor,
    obterPerfilCorretorLocal,
    atualizarPerfilCorretorLocal,
    encerrarSessaoCorretor,
} from '../utils/authCorretor';
import ModalImovelCorretor from '../components/ModalImovelCorretor';

const IMAGEM_PADRAO =
    'https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=600&q=80';

const formatarMoeda = (valor) => {
    if (!valor || Number(valor) <= 0) return 'Sob Consulta';
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        maximumFractionDigits: 0,
    }).format(valor);
};

const filtrarImoveisCarteira = (lista, termoBusca, filtroStatus) => {
    const termo = termoBusca.trim().toLowerCase();
    return lista.filter((imovel) => {
        const ehAtivo = imovel.ativo !== false;
        if (filtroStatus === 'ativos' && !ehAtivo) return false;
        if (filtroStatus === 'inativos' && ehAtivo) return false;

        if (!termo) return true;
        const titulo = (imovel.titulo || '').toLowerCase();
        const codigo = (imovel.codigo_original || '').toLowerCase();
        const bairro = (imovel.bairro || '').toLowerCase();
        return titulo.includes(termo) || codigo.includes(termo) || bairro.includes(termo);
    });
};

const CabecalhoPainelCorretor = ({ corretor, onNovoImovel, onLogout }) => (
    <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 rounded-3xl p-6 sm:p-8 text-white shadow-md mb-6 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div className="flex items-start sm:items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-blue-500/20 border border-blue-400/30 flex items-center justify-center text-blue-300 shrink-0">
                <Building2 size={28} />
            </div>
            <div>
                <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-400/30">
                        Parceiro Verificado
                    </span>
                    {corretor?.creci && (
                        <span className="text-[11px] font-semibold px-2.5 py-0.5 rounded-full bg-white/10 text-blue-100">
                            CRECI: {corretor.creci}
                        </span>
                    )}
                </div>
                <h1 className="text-xl sm:text-2xl font-extrabold mt-1.5">
                    {corretor?.imobiliaria || corretor?.nome || 'Área do Corretor'}
                </h1>
                <p className="text-xs sm:text-sm text-blue-200/80 mt-0.5">
                    Responsável: <strong className="text-white">{corretor?.nome}</strong> ({corretor?.usuario})
                </p>
            </div>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
            <button
                type="button"
                onClick={onNovoImovel}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white text-xs sm:text-sm font-extrabold shadow-sm transition-all"
            >
                <Plus size={17} />
                <span>Cadastrar Imóvel</span>
            </button>

            <Link
                to="/estatisticas"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs sm:text-sm font-bold shadow-sm transition-all"
            >
                <BarChart3 size={16} />
                <span>Inteligência de Mercado</span>
                <ArrowUpRight size={15} />
            </Link>

            <button
                type="button"
                onClick={onLogout}
                className="inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs sm:text-sm font-semibold border border-white/15 transition-all"
            >
                <LogOut size={16} />
                <span>Sair</span>
            </button>
        </div>
    </div>
);

const ResumoMetricasCorretor = ({ resumoConta, creditosImpulsionamento }) => (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="bg-white rounded-2xl border border-gray-200/90 p-5 shadow-sm flex items-center justify-between">
            <div>
                <span className="text-xs font-bold uppercase tracking-wider text-gray-400">
                    Imóveis Ativos na Vitrine
                </span>
                <p className="text-2xl sm:text-3xl font-extrabold text-gray-900 mt-1">
                    {resumoConta.imoveis_ativos}
                </p>
                <span className="text-xs text-gray-500">
                    {resumoConta.imoveis_inativos} pausados/inativos
                </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
                <Home size={24} />
            </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200/90 p-5 shadow-sm flex items-center justify-between">
            <div>
                <span className="text-xs font-bold uppercase tracking-wider text-gray-400">
                    Cliques & Leads Gerados
                </span>
                <p className="text-2xl sm:text-3xl font-extrabold text-emerald-600 mt-1">
                    {resumoConta.cliques_totais}
                </p>
                <span className="text-xs text-gray-500">
                    Interessados redirecionados aos seus anúncios
                </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                <MousePointerClick size={24} />
            </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200/90 p-5 shadow-sm flex items-center justify-between">
            <div>
                <span className="text-xs font-bold uppercase tracking-wider text-gray-400">
                    Destaques / Impulsionamento
                </span>
                <p className="text-2xl sm:text-3xl font-extrabold text-amber-600 mt-1">
                    {creditosImpulsionamento}
                </p>
                <span className="text-xs text-gray-500">
                    Créditos disponíveis para topo das buscas
                </span>
            </div>
            <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
                <Sparkles size={24} />
            </div>
        </div>
    </div>
);

const ItemImovelCarteira = ({
    imovel,
    onEditar,
    onAlternarStatus,
    onExcluir,
}) => {
    const ativo = imovel.ativo !== false;
    const fotoCapa = imovel.fotos?.[0] || IMAGEM_PADRAO;
    const temQueda =
        Number(imovel.preco_anterior || 0) > Number(imovel.preco || 0) &&
        Number(imovel.preco || 0) > 0;

    return (
        <div className="bg-white rounded-2xl border border-gray-200/90 p-4 shadow-sm hover:border-blue-200 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div className="flex items-start sm:items-center gap-4 min-w-0 flex-1">
                <img
                    src={fotoCapa}
                    alt={imovel.titulo}
                    onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = IMAGEM_PADRAO;
                    }}
                    className={`w-24 h-24 rounded-xl object-cover shrink-0 bg-gray-100 ${
                        ativo ? '' : 'grayscale opacity-65'
                    }`}
                />

                <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-1.5 mb-1">
                        <span
                            className={`px-2 py-0.5 rounded-md text-[10px] font-extrabold uppercase ${
                                ativo
                                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                    : 'bg-amber-50 text-amber-700 border border-amber-200'
                            }`}
                        >
                            {ativo ? 'Ativo na Vitrine' : 'Pausado / Inativo'}
                        </span>
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold uppercase bg-blue-50 text-blue-700">
                            {imovel.modalidade}
                        </span>
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-semibold bg-gray-100 text-gray-700">
                            {imovel.tipo}
                        </span>
                        <span className="text-[11px] text-gray-400 font-medium">
                            Cód. {imovel.codigo_original}
                        </span>
                    </div>

                    <h3 className="text-sm sm:text-base font-extrabold text-gray-900 truncate">
                        {imovel.titulo}
                    </h3>

                    <p className="text-xs text-gray-500 mt-0.5 truncate">
                        {imovel.bairro} • {imovel.cidade} | {imovel.quartos || 0} qts •{' '}
                        {imovel.banheiros || 0} banh • {imovel.vagas || 0} vagas
                    </p>

                    <div className="flex flex-wrap items-center gap-3 mt-2">
                        <div className="flex items-baseline gap-2">
                            <span className="text-base font-extrabold text-blue-600">
                                {formatarMoeda(imovel.preco)}
                            </span>
                            {temQueda && (
                                <span className="inline-flex items-center gap-0.5 text-xs text-rose-600 font-bold">
                                    <TrendingDown size={12} />
                                    <span className="line-through text-gray-400 font-normal">
                                        {formatarMoeda(imovel.preco_anterior)}
                                    </span>
                                </span>
                            )}
                        </div>

                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-lg">
                            <MousePointerClick size={12} />
                            <span>{imovel.cliques || 0} cliques</span>
                        </span>
                    </div>
                </div>
            </div>

            <div className="flex flex-wrap sm:flex-nowrap items-center gap-2 w-full sm:w-auto justify-end border-t sm:border-t-0 pt-3 sm:pt-0 border-gray-100">
                <button
                    type="button"
                    onClick={() => onEditar(imovel)}
                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-bold transition-colors"
                >
                    <Pencil size={14} />
                    <span>Editar / Preço</span>
                </button>

                <button
                    type="button"
                    onClick={() => onAlternarStatus(imovel)}
                    title={ativo ? 'Pausar exibição do imóvel' : 'Reativar imóvel na vitrine'}
                    className={`inline-flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-colors ${
                        ativo
                            ? 'bg-amber-50 hover:bg-amber-100 text-amber-800'
                            : 'bg-emerald-50 hover:bg-emerald-100 text-emerald-700'
                    }`}
                >
                    <Power size={14} />
                    <span>{ativo ? 'Pausar' : 'Ativar'}</span>
                </button>

                <Link
                    to={`/imovel/${imovel.id_unico}`}
                    title="Visualizar página pública do imóvel"
                    className="p-2 rounded-xl bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors"
                >
                    <Eye size={15} />
                </Link>

                <button
                    type="button"
                    onClick={() => onExcluir(imovel)}
                    title="Excluir imóvel permanentemente"
                    className="p-2 rounded-xl bg-rose-50 hover:bg-rose-100 text-rose-600 transition-colors"
                >
                    <Trash2 size={15} />
                </button>
            </div>
        </div>
    );
};

const AbaCarteiraImoveis = ({
    imoveis,
    carregandoImoveis,
    onNovoImovel,
    onEditarImovel,
    onAlternarStatus,
    onExcluirImovel,
}) => {
    const [busca, setBusca] = useState('');
    const [filtroStatus, setFiltroStatus] = useState('todos');

    const filtrados = useMemo(
        () => filtrarImoveisCarteira(imoveis, busca, filtroStatus),
        [imoveis, busca, filtroStatus]
    );

    return (
        <div className="space-y-4">
            <div className="bg-white rounded-2xl border border-gray-200/90 p-4 shadow-sm flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
                <div className="relative flex-1">
                    <Search
                        size={16}
                        className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"
                    />
                    <input
                        type="text"
                        aria-label="Buscar nos meus imóveis"
                        placeholder="Buscar por título, código ou bairro..."
                        value={busca}
                        onChange={(e) => setBusca(e.target.value)}
                        className="w-full pl-9 pr-4 py-2 rounded-xl border border-gray-200 bg-gray-50 text-xs sm:text-sm text-gray-800 focus:bg-white focus:border-blue-600 focus:outline-none"
                    />
                </div>

                <div className="flex items-center gap-2">
                    {[
                        { id: 'todos', label: `Todos (${imoveis.length})` },
                        {
                            id: 'ativos',
                            label: `Ativos (${imoveis.filter((i) => i.ativo !== false).length})`,
                        },
                        {
                            id: 'inativos',
                            label: `Pausados (${imoveis.filter((i) => i.ativo === false).length})`,
                        },
                    ].map((op) => (
                        <button
                            key={op.id}
                            type="button"
                            onClick={() => setFiltroStatus(op.id)}
                            className={`px-3 py-2 rounded-xl text-xs font-bold border transition-all ${
                                filtroStatus === op.id
                                    ? 'bg-slate-900 text-white border-slate-900'
                                    : 'bg-gray-50 text-gray-600 border-gray-200 hover:bg-gray-100'
                            }`}
                        >
                            {op.label}
                        </button>
                    ))}
                </div>
            </div>

            {carregandoImoveis && (
                <div className="bg-white rounded-3xl border border-gray-200 p-12 text-center text-sm text-gray-500">
                    Carregando sua carteira de imóveis...
                </div>
            )}

            {!carregandoImoveis && filtrados.length === 0 && (
                <div className="bg-white rounded-3xl border border-gray-200 p-12 text-center shadow-sm">
                    <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mx-auto mb-3">
                        <Home size={28} />
                    </div>
                    <h3 className="text-base sm:text-lg font-extrabold text-gray-900">
                        {imoveis.length === 0
                            ? 'Você ainda não cadastrou imóveis próprios'
                            : 'Nenhum imóvel encontrado para este filtro'}
                    </h3>
                    <p className="text-xs sm:text-sm text-gray-500 mt-1 max-w-md mx-auto">
                        {imoveis.length === 0
                            ? 'Clique no botão abaixo para publicar seu primeiro imóvel com fotos, valor e contato direto no seu WhatsApp.'
                            : 'Tente limpar o termo de busca ou alternar o filtro de status.'}
                    </p>
                    {imoveis.length === 0 && (
                        <button
                            type="button"
                            onClick={onNovoImovel}
                            className="mt-5 inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs sm:text-sm font-extrabold shadow-sm transition-all"
                        >
                            <Plus size={18} />
                            <span>Cadastrar Meu Primeiro Imóvel</span>
                        </button>
                    )}
                </div>
            )}

            {!carregandoImoveis &&
                filtrados.map((imovel) => (
                    <ItemImovelCarteira
                        key={imovel.id_unico}
                        imovel={imovel}
                        onEditar={onEditarImovel}
                        onAlternarStatus={onAlternarStatus}
                        onExcluir={onExcluirImovel}
                    />
                ))}
        </div>
    );
};

const FormularioContatoProfissional = ({ formPerfil, onChangeCampo, onSalvarPerfil, salvando }) => (
    <form
        onSubmit={onSalvarPerfil}
        className="bg-white rounded-3xl border border-gray-200/90 p-6 sm:p-8 shadow-sm space-y-5"
    >
        <div>
            <h2 className="text-lg font-extrabold text-gray-900">
                Meus Dados Comerciais & Contato Direto
            </h2>
            <p className="text-xs sm:text-sm text-gray-500 mt-0.5">
                Estes dados serão exibidos nos seus imóveis para que os clientes entrem em contato direto com você (mesmo que você não possua site próprio).
            </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
                <label
                    htmlFor="perfil-input-nome"
                    className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-1.5"
                >
                    Nome do Responsável / Corretor
                </label>
                <input
                    id="perfil-input-nome"
                    type="text"
                    value={formPerfil.nome}
                    onChange={(e) => onChangeCampo('nome', e.target.value)}
                    className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-sm text-gray-900 focus:bg-white focus:border-blue-600 focus:outline-none"
                />
            </div>

            <div>
                <label
                    htmlFor="perfil-input-creci"
                    className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-1.5"
                >
                    Registro CRECI
                </label>
                <div className="relative">
                    <Award size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        id="perfil-input-creci"
                        type="text"
                        placeholder="Ex: MG-12345"
                        value={formPerfil.creci}
                        onChange={(e) => onChangeCampo('creci', e.target.value)}
                        className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm text-gray-900 focus:bg-white focus:border-blue-600 focus:outline-none"
                    />
                </div>
            </div>

            <div>
                <label
                    htmlFor="perfil-input-whatsapp"
                    className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-1.5"
                >
                    WhatsApp para Receber Leads
                </label>
                <div className="relative">
                    <Phone size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        id="perfil-input-whatsapp"
                        type="text"
                        placeholder="Ex: (32) 99999-9999"
                        value={formPerfil.whatsapp}
                        onChange={(e) => onChangeCampo('whatsapp', e.target.value)}
                        className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm text-gray-900 focus:bg-white focus:border-blue-600 focus:outline-none"
                    />
                </div>
            </div>

            <div>
                <label
                    htmlFor="perfil-input-telefone"
                    className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-1.5"
                >
                    Telefone Fixo / Secundário
                </label>
                <div className="relative">
                    <Phone size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        id="perfil-input-telefone"
                        type="text"
                        placeholder="Ex: (32) 3371-0000"
                        value={formPerfil.telefone}
                        onChange={(e) => onChangeCampo('telefone', e.target.value)}
                        className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm text-gray-900 focus:bg-white focus:border-blue-600 focus:outline-none"
                    />
                </div>
            </div>

            <div>
                <label
                    htmlFor="perfil-input-email"
                    className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-1.5"
                >
                    E-mail Comercial
                </label>
                <div className="relative">
                    <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        id="perfil-input-email"
                        type="email"
                        placeholder="contato@exemplo.com.br"
                        value={formPerfil.email}
                        onChange={(e) => onChangeCampo('email', e.target.value)}
                        className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm text-gray-900 focus:bg-white focus:border-blue-600 focus:outline-none"
                    />
                </div>
            </div>

            <div>
                <label
                    htmlFor="perfil-input-site"
                    className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-1.5"
                >
                    Site ou Instagram (Opcional)
                </label>
                <div className="relative">
                    <Globe size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        id="perfil-input-site"
                        type="text"
                        placeholder="https://instagram.com/seuperfil"
                        value={formPerfil.site_externo}
                        onChange={(e) => onChangeCampo('site_externo', e.target.value)}
                        className="w-full pl-10 pr-3.5 py-2.5 rounded-xl border border-gray-200 bg-gray-50 text-sm text-gray-900 focus:bg-white focus:border-blue-600 focus:outline-none"
                    />
                </div>
            </div>
        </div>

        <div className="pt-2 flex justify-end">
            <button
                type="submit"
                disabled={salvando}
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-xs sm:text-sm font-bold shadow-sm transition-all"
            >
                <Save size={16} />
                <span>{salvando ? 'Salvando alterações...' : 'Salvar Dados de Contato'}</span>
            </button>
        </div>
    </form>
);

const FormularioAlterarSenha = ({ formSenha, onChangeSenha, onSalvarSenha, salvando }) => (
    <form
        onSubmit={onSalvarSenha}
        className="bg-white rounded-3xl border border-gray-200/90 p-6 sm:p-8 shadow-sm space-y-5"
    >
        <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-slate-100 text-slate-700 flex items-center justify-center">
                <Lock size={18} />
            </div>
            <div>
                <h2 className="text-base font-extrabold text-gray-900">
                    Alterar Senha de Acesso
                </h2>
                <p className="text-xs text-gray-500">
                    Mantenha sua conta segura atualizando sua senha periodicamente.
                </p>
            </div>
        </div>

        <div className="space-y-4">
            <div>
                <label
                    htmlFor="perfil-input-senha-atual"
                    className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-1.5"
                >
                    Senha Atual
                </label>
                <input
                    id="perfil-input-senha-atual"
                    type="password"
                    autoComplete="current-password"
                    value={formSenha.senha_atual}
                    onChange={(e) => onChangeSenha('senha_atual', e.target.value)}
                    className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-sm text-gray-900 focus:bg-white focus:border-blue-600 focus:outline-none"
                />
            </div>

            <div>
                <label
                    htmlFor="perfil-input-nova-senha"
                    className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-1.5"
                >
                    Nova Senha (mínimo 6 caracteres)
                </label>
                <input
                    id="perfil-input-nova-senha"
                    type="password"
                    autoComplete="new-password"
                    value={formSenha.nova_senha}
                    onChange={(e) => onChangeSenha('nova_senha', e.target.value)}
                    className="w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-sm text-gray-900 focus:bg-white focus:border-blue-600 focus:outline-none"
                />
            </div>
        </div>

        <button
            type="submit"
            disabled={salvando}
            className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 disabled:bg-slate-400 text-white text-xs sm:text-sm font-bold transition-all"
        >
            <Lock size={15} />
            <span>{salvando ? 'Atualizando...' : 'Atualizar Senha'}</span>
        </button>
    </form>
);

const PainelCorretor = () => {
    const navigate = useNavigate();
    const [abaAtiva, setAbaAtiva] = useState('imoveis');
    const [corretor, setCorretor] = useState(() => obterPerfilCorretorLocal());
    const [resumoConta, setResumoConta] = useState({
        imoveis_ativos: 0,
        imoveis_inativos: 0,
        cliques_totais: 0,
    });
    const [meusImoveis, setMeusImoveis] = useState([]);
    const [carregando, setCarregando] = useState(true);
    const [carregandoImoveis, setCarregandoImoveis] = useState(true);
    const [salvando, setSalvando] = useState(false);
    const [mensagemSucesso, setMensagemSucesso] = useState('');
    const [mensagemErro, setMensagemErro] = useState('');

    // Modal de criação/edição de imóvel
    const [modalAberto, setModalAberto] = useState(false);
    const [imovelEmEdicao, setImovelEmEdicao] = useState(null);

    const [formPerfil, setFormPerfil] = useState({
        nome: '',
        creci: '',
        whatsapp: '',
        telefone: '',
        email: '',
        site_externo: '',
    });

    const [formSenha, setFormSenha] = useState({
        senha_atual: '',
        nova_senha: '',
    });

    const exibirFeedback = useCallback((sucesso, erro = '') => {
        setMensagemSucesso(sucesso);
        setMensagemErro(erro);
        if (sucesso) {
            setTimeout(() => setMensagemSucesso(''), 4000);
        }
    }, []);

    const recarregarCarteira = useCallback(async () => {
        setCarregandoImoveis(true);
        try {
            const [resPerfil, resImoveis] = await Promise.all([
                obterMeuPerfilCorretorApi(),
                listarMeusImoveisCorretorApi(),
            ]);
            if (resPerfil?.corretor) {
                setCorretor(resPerfil.corretor);
                atualizarPerfilCorretorLocal(resPerfil.corretor);
                setFormPerfil({
                    nome: resPerfil.corretor.nome || '',
                    creci: resPerfil.corretor.creci || '',
                    whatsapp: resPerfil.corretor.whatsapp || '',
                    telefone: resPerfil.corretor.telefone || '',
                    email: resPerfil.corretor.email || '',
                    site_externo: resPerfil.corretor.site_externo || '',
                });
            }
            if (resPerfil?.resumo_conta) {
                setResumoConta(resPerfil.resumo_conta);
            }
            if (Array.isArray(resImoveis?.data)) {
                setMeusImoveis(resImoveis.data);
            }
        } catch (error) {
            if (error.status === 401) {
                navigate('/corretor/login', { replace: true });
            }
        } finally {
            setCarregando(false);
            setCarregandoImoveis(false);
        }
    }, [navigate]);

    useEffect(() => {
        if (!estaAutenticadoCorretor()) {
            navigate('/corretor/login', { replace: true });
            return;
        }
        void recarregarCarteira();
    }, [navigate, recarregarCarteira]);

    const handleLogout = () => {
        encerrarSessaoCorretor();
        navigate('/corretor/login', { replace: true });
    };

    const handleAbrirNovoImovel = () => {
        setImovelEmEdicao(null);
        setModalAberto(true);
    };

    const handleAbrirEdicaoImovel = (imovel) => {
        setImovelEmEdicao(imovel);
        setModalAberto(true);
    };

    const handleSalvarImovelModal = async (payload) => {
        exibirFeedback('', '');
        setSalvando(true);
        try {
            if (imovelEmEdicao?.id_unico) {
                await editarImovelCorretorApi(imovelEmEdicao.id_unico, payload);
                exibirFeedback('Imóvel atualizado com sucesso!');
            } else {
                await cadastrarImovelCorretorApi(payload);
                exibirFeedback('Novo imóvel publicado com sucesso!');
            }
            setModalAberto(false);
            setImovelEmEdicao(null);
            await recarregarCarteira();
        } catch (error) {
            exibirFeedback('', error.message || 'Erro ao salvar o imóvel.');
        } finally {
            setSalvando(false);
        }
    };

    const handleAlternarStatusImovel = async (imovel) => {
        const novoAtivo = imovel.ativo === false;
        exibirFeedback('', '');
        try {
            await alterarStatusImovelCorretorApi(imovel.id_unico, novoAtivo);
            exibirFeedback(
                novoAtivo ? 'Imóvel reativado na vitrine!' : 'Imóvel pausado com sucesso.'
            );
            await recarregarCarteira();
        } catch (error) {
            exibirFeedback('', error.message || 'Erro ao alterar status do imóvel.');
        }
    };

    const handleExcluirImovel = async (imovel) => {
        const confirmar = globalThis.confirm(
            `Tem certeza que deseja excluir permanentemente o imóvel "${imovel.titulo}" (Cód. ${imovel.codigo_original})?`
        );
        if (!confirmar) return;

        exibirFeedback('', '');
        try {
            await excluirImovelCorretorApi(imovel.id_unico);
            exibirFeedback('Imóvel excluído da sua carteira.');
            await recarregarCarteira();
        } catch (error) {
            exibirFeedback('', error.message || 'Erro ao excluir o imóvel.');
        }
    };

    const handleSalvarPerfil = async (e) => {
        e.preventDefault();
        exibirFeedback('', '');
        setSalvando(true);
        try {
            const res = await atualizarPerfilCorretorApi(formPerfil);
            if (res?.corretor) {
                setCorretor(res.corretor);
                atualizarPerfilCorretorLocal(res.corretor);
            }
            exibirFeedback('Dados de contato atualizados com sucesso!');
        } catch (error) {
            exibirFeedback('', error.message || 'Erro ao salvar alterações.');
        } finally {
            setSalvando(false);
        }
    };

    const handleSalvarSenha = async (e) => {
        e.preventDefault();
        exibirFeedback('', '');
        if (!formSenha.senha_atual || !formSenha.nova_senha) {
            exibirFeedback('', 'Informe sua senha atual e a nova senha.');
            return;
        }
        if (formSenha.nova_senha.length < 6) {
            exibirFeedback('', 'A nova senha deve ter pelo menos 6 caracteres.');
            return;
        }

        setSalvando(true);
        try {
            await atualizarPerfilCorretorApi(formSenha);
            setFormSenha({ senha_atual: '', nova_senha: '' });
            exibirFeedback('Senha alterada com sucesso!');
        } catch (error) {
            exibirFeedback('', error.message || 'Erro ao alterar a senha.');
        } finally {
            setSalvando(false);
        }
    };

    if (carregando && !corretor) {
        return (
            <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 text-center text-sm text-gray-500">
                Carregando painel do corretor...
            </main>
        );
    }

    return (
        <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <CabecalhoPainelCorretor
                corretor={corretor}
                onNovoImovel={handleAbrirNovoImovel}
                onLogout={handleLogout}
            />

            {mensagemSucesso && (
                <div className="mb-6 p-4 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center gap-2.5 text-emerald-800 text-sm font-semibold">
                    <CheckCircle2 size={18} className="text-emerald-600 shrink-0" />
                    <span>{mensagemSucesso}</span>
                </div>
            )}

            {mensagemErro && (
                <div className="mb-6 p-4 rounded-2xl bg-rose-50 border border-rose-200 flex items-center gap-2.5 text-rose-700 text-sm font-semibold">
                    <AlertCircle size={18} className="text-rose-600 shrink-0" />
                    <span>{mensagemErro}</span>
                </div>
            )}

            <ResumoMetricasCorretor
                resumoConta={resumoConta}
                creditosImpulsionamento={corretor?.creditos_impulsionamento || 0}
            />

            {/* Navegação por Abas Internas */}
            <div className="flex items-center gap-2 mb-6 border-b border-gray-200 pb-3">
                <button
                    type="button"
                    onClick={() => setAbaAtiva('imoveis')}
                    className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all ${
                        abaAtiva === 'imoveis'
                            ? 'bg-blue-600 text-white shadow-sm'
                            : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                    }`}
                >
                    <Home size={16} />
                    <span>Meus Imóveis ({meusImoveis.length})</span>
                </button>

                <button
                    type="button"
                    onClick={() => setAbaAtiva('perfil')}
                    className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all ${
                        abaAtiva === 'perfil'
                            ? 'bg-blue-600 text-white shadow-sm'
                            : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
                    }`}
                >
                    <UserCog size={16} />
                    <span>Meus Dados & Senha</span>
                </button>
            </div>

            {abaAtiva === 'imoveis' && (
                <AbaCarteiraImoveis
                    imoveis={meusImoveis}
                    carregandoImoveis={carregandoImoveis}
                    onNovoImovel={handleAbrirNovoImovel}
                    onEditarImovel={handleAbrirEdicaoImovel}
                    onAlternarStatus={handleAlternarStatusImovel}
                    onExcluirImovel={handleExcluirImovel}
                />
            )}

            {abaAtiva === 'perfil' && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                    <div className="lg:col-span-8">
                        <FormularioContatoProfissional
                            formPerfil={formPerfil}
                            onChangeCampo={(campo, valor) =>
                                setFormPerfil((prev) => ({ ...prev, [campo]: valor }))
                            }
                            onSalvarPerfil={handleSalvarPerfil}
                            salvando={salvando}
                        />
                    </div>

                    <div className="lg:col-span-4 space-y-6">
                        <FormularioAlterarSenha
                            formSenha={formSenha}
                            onChangeSenha={(campo, valor) =>
                                setFormSenha((prev) => ({ ...prev, [campo]: valor }))
                            }
                            onSalvarSenha={handleSalvarSenha}
                            salvando={salvando}
                        />
                    </div>
                </div>
            )}

            <ModalImovelCorretor
                aberto={modalAberto}
                imovelEdicao={imovelEmEdicao}
                corretor={corretor}
                salvando={salvando}
                onFechar={() => {
                    setModalAberto(false);
                    setImovelEmEdicao(null);
                }}
                onSalvar={handleSalvarImovelModal}
            />
        </main>
    );
};

export default PainelCorretor;
