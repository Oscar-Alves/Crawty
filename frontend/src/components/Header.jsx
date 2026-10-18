import { useState, useEffect } from 'react';
import { Home, BarChart3, Search, Flame } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { lerIdsMatchesCookie } from '../utils/cookiesMatch';

const Header = () => {
    const location = useLocation();
    const isEstatisticas = location.pathname.startsWith('/estatisticas');
    const isMatch = location.pathname.startsWith('/match');
    const isBusca = location.pathname === '/' || location.pathname.startsWith('/imovel');
    const [totalMatches, setTotalMatches] = useState(() => lerIdsMatchesCookie().length);

    useEffect(() => {
        const aoAtualizarMatches = (evento) => {
            const lista = evento?.detail;
            if (Array.isArray(lista)) {
                setTotalMatches(lista.length);
            } else {
                setTotalMatches(lerIdsMatchesCookie().length);
            }
        };

        globalThis.addEventListener('crawty-matches-updated', aoAtualizarMatches);
        return () => globalThis.removeEventListener('crawty-matches-updated', aoAtualizarMatches);
    }, []);

    return (
        <header className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm backdrop-blur-md bg-opacity-95">
            <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-3">
                <Link to="/" className="flex items-center gap-2 hover:opacity-85 transition-opacity shrink-0">
                    <div className="bg-blue-600 p-1.5 rounded-lg shadow-sm">
                        <Home className="text-white" size={20} />
                    </div>
                    <h1 className="text-xl font-extrabold text-blue-600 tracking-tight">
                        Hub<span className="text-gray-900">Imóveis</span>
                    </h1>
                </Link>

                <nav className="flex items-center gap-1.5 sm:gap-2">
                    <Link
                        to="/"
                        className={`inline-flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                            isBusca
                                ? 'bg-blue-50 text-blue-700 border border-blue-200/80'
                                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                        }`}
                    >
                        <Search size={15} />
                        <span className="hidden sm:inline">Buscar Imóveis</span>
                        <span className="sm:hidden">Buscar</span>
                    </Link>

                    <Link
                        to="/match"
                        className={`inline-flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                            isMatch
                                ? 'bg-gradient-to-r from-rose-500 to-pink-600 text-white shadow-sm'
                                : 'text-rose-600 hover:bg-rose-50 border border-rose-200/70'
                        }`}
                    >
                        <Flame size={15} />
                        <span>Modo Match</span>
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

                    <Link
                        to="/estatisticas"
                        className={`inline-flex items-center gap-1.5 px-3 sm:px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all ${
                            isEstatisticas
                                ? 'bg-blue-600 text-white shadow-sm'
                                : 'text-gray-700 hover:text-blue-600 hover:bg-blue-50/60 border border-transparent hover:border-blue-100'
                        }`}
                    >
                        <BarChart3 size={15} />
                        <span className="hidden md:inline">Mercado & Dados</span>
                        <span className="md:hidden">Dados</span>
                    </Link>
                </nav>
            </div>
        </header>
    );
};

export default Header;