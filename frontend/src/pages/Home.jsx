import { useState, useEffect } from 'react';
import { SearchX, Loader2 } from 'lucide-react';
import ImovelCard from '../components/ImovelCard';
import Filtros from '../components/Filtros';
import { getImoveis, getFiltros } from '../services/api';

const Home = () => {
    const [imoveis, setImoveis] = useState([]);
    const [opcoesFiltro, setOpcoesFiltro] = useState({ cidades: [], bairros: [], tipos: [] });
    const [loading, setLoading] = useState(true);
    const [meta, setMeta] = useState({ total: 0, page: 1, pages: 1 });
    
    const [filtros, setFiltros] = useState({
        cidade: '',
        bairro: '',
        modalidade: '',
        tipo: '',
        ordenar_por: ''
    });

    // Carregar opções iniciais
    useEffect(() => {
        getFiltros().then(data => setOpcoesFiltro(data));
    }, []);

    // Carregar imóveis com debounce
    useEffect(() => {
        const fetchDados = async () => {
            setLoading(true);
            try {
                const dados = await getImoveis({ 
                    page: meta.page, 
                    limit: 12, 
                    ...filtros 
                });
                setImoveis(dados.data);
                setMeta(dados.meta);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };

        const timeoutId = setTimeout(fetchDados, 300);
        return () => clearTimeout(timeoutId);
    }, [filtros, meta.page]);

    const mudarPagina = (novaPagina) => {
        if (novaPagina >= 1 && novaPagina <= meta.pages) {
            setMeta(prev => ({ ...prev, page: novaPagina }));
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Filtros opcoes={opcoesFiltro} filtros={filtros} setFiltros={setFiltros} />

            <div className="mb-4 flex justify-between items-center">
                <h2 className="text-gray-700 font-medium">Resultados da busca</h2>
                <span className="bg-blue-100 text-blue-800 text-xs font-bold px-2.5 py-0.5 rounded-full">
                    {loading ? '...' : meta.total} encontrados
                </span>
            </div>

            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {[...Array(8)].map((_, i) => (
                        <div key={i} className="bg-white rounded-xl h-[400px] animate-pulse border border-gray-200">
                            <div className="h-48 bg-gray-200 rounded-t-xl"></div>
                            <div className="p-4 space-y-3">
                                <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                            </div>
                        </div>
                    ))}
                </div>
            ) : imoveis.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {imoveis.map(imovel => (
                        <ImovelCard key={imovel.id_unico} imovel={imovel} />
                    ))}
                </div>
            ) : (
                <div className="text-center py-20 bg-white rounded-xl border border-gray-100 border-dashed">
                    <SearchX size={64} className="mx-auto text-gray-300 mb-4" />
                    <h3 className="text-xl font-medium text-gray-900 mb-1">Nenhum imóvel encontrado</h3>
                    <p className="text-gray-500">Tente ajustar seus filtros de busca.</p>
                    <button 
                        onClick={() => setFiltros({cidade: '', bairro: '', modalidade: '', tipo: '', ordenar_por: ''})}
                        className="mt-4 text-blue-600 hover:underline font-medium"
                    >
                        Limpar filtros
                    </button>
                </div>
            )}

            {!loading && meta.pages > 1 && (
                <div className="mt-12 flex justify-center gap-3">
                    <button onClick={() => mudarPagina(meta.page - 1)} disabled={meta.page === 1} className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50">Anterior</button>
                    <span className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border rounded-lg">Página {meta.page} de {meta.pages}</span>
                    <button onClick={() => mudarPagina(meta.page + 1)} disabled={meta.page === meta.pages} className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50">Próxima</button>
                </div>
            )}
        </div>
    );
};

export default Home;