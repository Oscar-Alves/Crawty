import { useState, useEffect } from 'react';
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
} from 'lucide-react';
import { obterMeuPerfilCorretorApi, atualizarPerfilCorretorApi } from '../services/api';
import {
    estaAutenticadoCorretor,
    obterPerfilCorretorLocal,
    atualizarPerfilCorretorLocal,
    encerrarSessaoCorretor,
} from '../utils/authCorretor';

const CabecalhoPainelCorretor = ({ corretor, onLogout }) => (
    <div className="bg-gradient-to-r from-slate-900 via-blue-950 to-indigo-950 rounded-3xl p-6 sm:p-8 text-white shadow-md mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
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

        <div className="flex flex-wrap items-center gap-3">
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
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs sm:text-sm font-semibold border border-white/15 transition-all"
            >
                <LogOut size={16} />
                <span>Sair</span>
            </button>
        </div>
    </div>
);

const ResumoMetricasCorretor = ({ resumoConta, creditosImpulsionamento }) => (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-2xl border border-gray-200/90 p-5 shadow-sm flex items-center justify-between">
            <div>
                <span className="text-xs font-bold uppercase tracking-wider text-gray-400">
                    Imóveis Ativos na Vitrine
                </span>
                <p className="text-2xl sm:text-3xl font-extrabold text-gray-900 mt-1">
                    {resumoConta.imoveis_ativos}
                </p>
                <span className="text-xs text-gray-500">
                    {resumoConta.imoveis_inativos} encerrados/inativos no histórico
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
    const [corretor, setCorretor] = useState(() => obterPerfilCorretorLocal());
    const [resumoConta, setResumoConta] = useState({
        imoveis_ativos: 0,
        imoveis_inativos: 0,
        cliques_totais: 0,
    });
    const [carregando, setCarregando] = useState(true);
    const [salvando, setSalvando] = useState(false);
    const [mensagemSucesso, setMensagemSucesso] = useState('');
    const [mensagemErro, setMensagemErro] = useState('');

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

    useEffect(() => {
        if (!estaAutenticadoCorretor()) {
            navigate('/corretor/login', { replace: true });
            return undefined;
        }

        let ativo = true;
        obterMeuPerfilCorretorApi()
            .then((dados) => {
                if (!ativo) return;
                if (dados?.corretor) {
                    setCorretor(dados.corretor);
                    atualizarPerfilCorretorLocal(dados.corretor);
                    setFormPerfil({
                        nome: dados.corretor.nome || '',
                        creci: dados.corretor.creci || '',
                        whatsapp: dados.corretor.whatsapp || '',
                        telefone: dados.corretor.telefone || '',
                        email: dados.corretor.email || '',
                        site_externo: dados.corretor.site_externo || '',
                    });
                }
                if (dados?.resumo_conta) {
                    setResumoConta(dados.resumo_conta);
                }
            })
            .catch((err) => {
                if (!ativo) return;
                if (err.status === 401) {
                    navigate('/corretor/login', { replace: true });
                }
            })
            .finally(() => {
                if (ativo) setCarregando(false);
            });

        return () => {
            ativo = false;
        };
    }, [navigate]);

    const handleLogout = () => {
        encerrarSessaoCorretor();
        navigate('/corretor/login', { replace: true });
    };

    const exibirFeedback = (sucesso, erro = '') => {
        setMensagemSucesso(sucesso);
        setMensagemErro(erro);
        if (sucesso) {
            setTimeout(() => setMensagemSucesso(''), 4000);
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
        } catch (err) {
            exibirFeedback('', err.message || 'Erro ao salvar alterações.');
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
        } catch (err) {
            exibirFeedback('', err.message || 'Erro ao alterar a senha.');
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
            <CabecalhoPainelCorretor corretor={corretor} onLogout={handleLogout} />

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
                    <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-3xl p-6 text-white shadow-sm">
                        <div className="w-10 h-10 rounded-xl bg-white/15 flex items-center justify-center mb-3">
                            <BarChart3 size={20} />
                        </div>
                        <h3 className="text-base font-extrabold">
                            Inteligência de Mercado Exclusiva
                        </h3>
                        <p className="text-xs text-blue-100 mt-1 leading-relaxed">
                            Consulte o valor médio do m² por bairro, estoque de concorrentes e faixas de preço mais procuradas em São João del Rei e região.
                        </p>
                        <Link
                            to="/estatisticas"
                            className="mt-4 w-full inline-flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-white text-blue-700 hover:bg-blue-50 text-xs font-extrabold transition-colors"
                        >
                            <span>Abrir Painel de Estatísticas</span>
                            <ArrowUpRight size={15} />
                        </Link>
                    </div>

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
        </main>
    );
};

export default PainelCorretor;

