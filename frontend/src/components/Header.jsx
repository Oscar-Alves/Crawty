import { useState, useEffect } from 'react';
import { Home, BarChart3, Search, Flame, Building2 } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { lerIdsMatchesCookie } from '../utils/cookiesMatch';
import { estaAutenticadoCorretor } from '../utils/authCorretor';

const Header = () => {
    const location = useLocation();
    const isEstatisticas = location.pathname.startsWith('/estatisticas');
    const isMatch = location.pathname.startsWith('/match');
    const isCorretor = location.pathname.startsWith('/corretor');
    const isBusca = location.pathname === '/' || location.pathname.startsWith('/imovel');

    const [totalMatches, setTotalMatches] = useState(() => lerIdsMatchesCookie().length);
    const [autenticadoCorretor, setAutenticadoCorretor] = useState(() => estaAutenticadoCorretor());

    useEffect(() => {
        const aoAtualizarMatches = (evento) => {
            const lista = evento?.detail;
            if (Array.isArray(lista)) {
                setTotalMatches(lista.length);
            } else {
                setTotalMatches(lerIdsMatchesCookie().length);
            }
        };

        const aoAtualizarAuth = () => {
            setAutenticadoCorretor(estaAutenticadoCorretor());
        };

        globalThis.addEventListener('crawty-matches-updated', aoAtualizarMatches);
        globalThis.addEventListener('crawty-auth-updated', aoAtualizarAuth);
        return () => {
            globalThis.removeEventListener('crawty-matches-updated', aoAtualizarMatches);
            globalThis.removeEventListener('crawty-auth-updated', aoAtualizarAuth);
        };
    }, []);

    return (
        <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm backdrop-blur-md bg-opacity-95 w-full">
            <div className="max-w-[1440px] mx-auto px-3 sm:px-6 lg:px-8 h-14 sm:h-16 flex items-center justify-between gap-1 sm:gap-3">
                <Link to="/" className="flex items-center gap-1.5 sm:gap-2 hover:opacity-85 transition-opacity shrink-0">
                    <div className="bg-blue-600 p-1 sm:p-1.5 rounded-lg shadow-sm">
                        <Home className="text-white w-4 h-4 sm:w-5 sm:h-5" />
                    </div>
                    <h1 className="text-base sm:text-xl font-extrabold text-blue-600 tracking-tight whitespace-nowrap">
                        Hub<span className="text-gray-900">Imóveis</span>
                    </h1>
                </Link>

                <nav className="flex items-center gap-1 sm:gap-2 shrink-0">
                    <Link
                        to="/"
                        title="Buscar Imóveis"
                        className={`inline-flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                            isBusca
                                ? 'bg-blue-50 text-blue-700 border border-blue-200/80'
                                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                        }`}
                    >
                        <Search size={15} />
                        <span className="hidden sm:inline">Buscar Imóveis</span>
                    </Link>

                    <Link
                        to="/match"
                        title="Modo Match"
                        className={`inline-flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                            isMatch
                                ? 'bg-gradient-to-r from-rose-500 to-pink-600 text-white shadow-sm'
                                : 'text-rose-600 hover:bg-rose-50 border border-rose-200/70'
                        }`}
                    >
                        <Flame size={15} />
                        <span><span className="hidden sm:inline">Modo </span>Match</span>
                        {totalMatches > 0 && (
                            <span
                                className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded-full ${
                                    isMatch
                                        ? 'bg-white/25 text-white'
                                        : 'bg-rose-100 text-rose-700'
                                }`}
                            >
                                {totalMatches}
                            </span>
                        )}
                    </Link>

                    {autenticadoCorretor && (
                        <Link
                            to="/estatisticas"
                            title="Mercado & Dados Estatísticos"
                            className={`inline-flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                                isEstatisticas
                                    ? 'bg-blue-600 text-white shadow-sm'
                                    : 'text-gray-700 hover:text-blue-600 hover:bg-blue-50/60 border border-transparent hover:border-blue-100'
                            }`}
                        >
                            <BarChart3 size={15} />
                            <span className="hidden md:inline">Mercado & Dados</span>
                            <span className="hidden sm:inline md:hidden">Dados</span>
                        </Link>
                    )}

                    <Link
                        to={autenticadoCorretor ? '/corretor' : '/corretor/login'}
                        title={autenticadoCorretor ? 'Painel do Corretor' : 'Área do Corretor'}
                        className={`inline-flex items-center gap-1 sm:gap-1.5 px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                            isCorretor
                                ? 'bg-slate-900 text-white shadow-sm'
                                : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100 border border-slate-200/80'
                        }`}
                    >
                        <Building2 size={15} />
                        <span className="hidden md:inline">
                            {autenticadoCorretor ? 'Painel Corretor' : 'Área do Corretor'}
                        </span>
                        <span className="hidden sm:inline md:hidden">Corretor</span>
                    </Link>
                </nav>
            </div>
        </header>
    );
};

export default Header;