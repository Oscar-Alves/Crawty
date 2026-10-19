import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import {
    Building2,
    Lock,
    User,
    ArrowRight,
    BarChart3,
    Sparkles,
    ShieldCheck,
    AlertCircle,
} from 'lucide-react';
import { loginCorretorApi } from '../services/api';
import { salvarSessaoCorretor, estaAutenticadoCorretor } from '../utils/authCorretor';

const DESTINOS_PERMITIDOS = new Set(['/corretor', '/estatisticas']);

const LoginCorretor = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const redirectParam = searchParams.get('redirect') || '/corretor';
    const destinoSeguro = DESTINOS_PERMITIDOS.has(redirectParam) ? redirectParam : '/corretor';

    const [usuario, setUsuario] = useState('');
    const [senha, setSenha] = useState('');
    const [carregando, setCarregando] = useState(false);
    const [erro, setErro] = useState('');

    useEffect(() => {
        if (estaAutenticadoCorretor()) {
            navigate(destinoSeguro, { replace: true });
        }
    }, [navigate, destinoSeguro]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErro('');

        if (!usuario.trim() || !senha) {
            setErro('Preencha seu usuário e senha para continuar.');
            return;
        }

        setCarregando(true);
        try {
            const resposta = await loginCorretorApi(usuario.trim(), senha);
            salvarSessaoCorretor(resposta.access_token, resposta.corretor);
            navigate(destinoSeguro, { replace: true });
        } catch (err) {
            setErro(err.message || 'Credenciais inválidas. Verifique seu usuário e senha.');
        } finally {
            setCarregando(false);
        }
    };

    return (
        <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14">
            <div className="grid grid-cols-1 lg:grid-cols-12 bg-white rounded-3xl border border-gray-200 shadow-lg overflow-hidden">
                {/* Coluna Esquerda: Apresentação Comercial B2B */}
                <div className="lg:col-span-6 bg-gradient-to-br from-slate-900 via-blue-950 to-indigo-950 text-white p-8 sm:p-10 flex flex-col justify-between">
                    <div>
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-200 text-xs font-bold uppercase tracking-wider mb-6">
                            <ShieldCheck size={15} />
                            <span>Portal Exclusivo para Parceiros</span>
                        </div>

                        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight leading-tight">
                            Área do Corretor & Imobiliárias Parceiras
                        </h1>
                        <p className="text-blue-100/85 text-sm mt-3 leading-relaxed">
                            Gerencie sua carteira de imóveis diretamente no HubImóveis, receba leads no seu WhatsApp e tome decisões baseadas nos dados reais do mercado regional.
                        </p>

                        <div className="mt-8 space-y-4">
                            <div className="flex items-start gap-3.5">
                                <div className="w-9 h-9 rounded-xl bg-blue-500/20 border border-blue-400/25 flex items-center justify-center text-blue-300 shrink-0 mt-0.5">
                                    <Building2 size={18} />
                                </div>
                                <div>
                                    <h2 className="text-sm font-bold text-white">
                                        Publique sem precisar de site próprio
                                    </h2>
                                    <p className="text-xs text-blue-100/75 mt-0.5">
                                        Ideal para corretores autônomos e imobiliárias: cadastre seus imóveis, edite preços e receba contatos diretos.
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-start gap-3.5">
                                <div className="w-9 h-9 rounded-xl bg-blue-500/20 border border-blue-400/25 flex items-center justify-center text-blue-300 shrink-0 mt-0.5">
                                    <BarChart3 size={18} />
                                </div>
                                <div>
                                    <h2 className="text-sm font-bold text-white">
                                        Inteligência de Mercado Exclusiva
                                    </h2>
                                    <p className="text-xs text-blue-100/75 mt-0.5">
                                        Acesso restrito ao painel de valorização por bairro, preço médio do m², liquidez e estoque da região.
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-start gap-3.5">
                                <div className="w-9 h-9 rounded-xl bg-blue-500/20 border border-blue-400/25 flex items-center justify-center text-blue-300 shrink-0 mt-0.5">
                                    <Sparkles size={18} />
                                </div>
                                <div>
                                    <h2 className="text-sm font-bold text-white">
                                        Impulsionamento e Destaque
                                    </h2>
                                    <p className="text-xs text-blue-100/75 mt-0.5">
                                        Posicione suas melhores oportunidades no topo das buscas e nas recomendações relevantes.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="mt-10 pt-6 border-t border-white/15">
                        <p className="text-xs text-blue-200 font-semibold">
                            Ainda não possui credenciais de parceiro?
                        </p>
                        <p className="text-xs text-blue-100/75 mt-1">
                            O acesso é liberado mediante credenciamento comercial. Entre em contato com a administração do HubImóveis para contratar seu plano.
                        </p>
                    </div>
                </div>

                {/* Coluna Direita: Formulário de Login */}
                <div className="lg:col-span-6 p-8 sm:p-10 flex flex-col justify-center">
                    <div className="max-w-sm mx-auto w-full">
                        <h2 className="text-xl sm:text-2xl font-extrabold text-gray-900">
                            Acesse sua conta
                        </h2>
                        <p className="text-xs sm:text-sm text-gray-500 mt-1">
                            Informe o usuário e a senha fornecidos no seu credenciamento.
                        </p>

                        {erro && (
                            <div className="mt-5 p-3.5 rounded-2xl bg-rose-50 border border-rose-200 flex items-start gap-2.5 text-rose-700 text-xs sm:text-sm">
                                <AlertCircle size={18} className="shrink-0 mt-0.5" />
                                <span>{erro}</span>
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="mt-6 space-y-5">
                            <div>
                                <label
                                    htmlFor="corretor-input-usuario"
                                    className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-2"
                                >
                                    Usuário
                                </label>
                                <div className="relative">
                                    <User
                                        size={17}
                                        className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"
                                    />
                                    <input
                                        id="corretor-input-usuario"
                                        type="text"
                                        autoComplete="username"
                                        placeholder="ex: joao.corretor"
                                        value={usuario}
                                        onChange={(e) => setUsuario(e.target.value)}
                                        className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-sm text-gray-900 focus:bg-white focus:border-blue-600 focus:outline-none transition-colors"
                                    />
                                </div>
                            </div>

                            <div>
                                <label
                                    htmlFor="corretor-input-senha"
                                    className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-2"
                                >
                                    Senha
                                </label>
                                <div className="relative">
                                    <Lock
                                        size={17}
                                        className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"
                                    />
                                    <input
                                        id="corretor-input-senha"
                                        type="password"
                                        autoComplete="current-password"
                                        placeholder="••••••••"
                                        value={senha}
                                        onChange={(e) => setSenha(e.target.value)}
                                        className="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-200 bg-gray-50 text-sm text-gray-900 focus:bg-white focus:border-blue-600 focus:outline-none transition-colors"
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={carregando}
                                className="w-full inline-flex items-center justify-center gap-2 py-3.5 px-6 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold text-sm shadow-sm transition-all"
                            >
                                <span>{carregando ? 'Autenticando...' : 'Entrar no Painel do Corretor'}</span>
                                {!carregando && <ArrowRight size={17} />}
                            </button>
                        </form>

                        <div className="mt-8 pt-6 border-t border-gray-100 text-center">
                            <Link
                                to="/"
                                className="text-xs font-semibold text-gray-500 hover:text-blue-600 transition-colors"
                            >
                                ← Voltar para a busca pública de imóveis
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
};

export default LoginCorretor;

