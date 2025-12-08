import { useState, useEffect } from 'react';
import { SearchX, Loader2 } from 'lucide-react';
import ImovelCard from '../components/ImovelCard';
import Filtros from '../components/Filtros';
import { getImoveis, getFiltros } from '../services/api';

const Home = () => {
    // 1. Tenta recuperar filtros salvos ou usa o padrão
    const [filtros, setFiltros] = useState(() => {
        const salvos = sessionStorage.getItem('crawty_filtros');
        return salvos ? JSON.parse(salvos) : {
            cidade: '',
            bairro: '',
            modalidade: '',
            tipo: '',
            ordenar_por: ''
        };
    });

    // 2. Tenta recuperar a página salva ou começa da 1
    const [meta, setMeta] = useState(() => {
        const paginaSalva = sessionStorage.getItem('crawty_page');
        return { 
            total: 0, 
            page: paginaSalva ? parseInt(paginaSalva) : 1, 
            pages: 1 
        };
    });

    const [imoveis, setImoveis] = useState([]);
    const [opcoesFiltro, setOpcoesFiltro] = useState({ cidades: [], bairros: [], tipos: [] });
    const [loading, setLoading] = useState(true);

    // 3. Salva no SessionStorage sempre que Filtros ou Página mudarem
    useEffect(() => {
        sessionStorage.setItem('crawty_filtros', JSON.stringify(filtros));
        sessionStorage.setItem('crawty_page', meta.page.toString());
    }, [filtros, meta.page]);

    // Carregar opções do backend (Cidades, Tipos...)
    useEffect(() => {
        getFiltros().then(data => setOpcoesFiltro(data));
    }, []);

    // Busca os imóveis quando filtros ou página mudam
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
                // Atualiza meta, mas preserva a página atual se a API retornar algo diferente (precaução)
                setMeta(prev => ({ ...dados.meta, page: prev.page }));
            } catch (error) {
                console.error("Erro ao buscar imóveis:", error);
            } finally {
                setLoading(false);
            }
        };

        const timeoutId = setTimeout(fetchDados, 300); // Debounce
        return () => clearTimeout(timeoutId);
    }, [filtros, meta.page]);

    // Função wrapper para resetar a página ao filtrar
    const handleFiltrosChange = (novoEstadoOuFuncao) => {
        setFiltros(prev => {
            const novosFiltros = typeof novoEstadoOuFuncao === 'function' 
                ? novoEstadoOuFuncao(prev) 
                : novoEstadoOuFuncao;
            
            // Se os filtros mudaram, volta para a página 1
            if (JSON.stringify(prev) !== JSON.stringify(novosFiltros)) {
                setMeta(m => ({ ...m, page: 1 }));
            }
            return novosFiltros;
        });
    };

    const mudarPagina = (novaPagina) => {
        setMeta(prev => ({ ...prev, page: novaPagina }));
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-800 mb-2">Encontre seu Imóvel Ideal</h1>
                <p className="text-gray-600">Busque as melhores opções em diversas imobiliárias de uma só vez.</p>
            </div>

            {/* Passamos o wrapper handleFiltrosChange em vez de setFiltros direto */}
            <Filtros 
                opcoes={opcoesFiltro} 
                filtros={filtros} 
                setFiltros={handleFiltrosChange} 
            />

            {loading ? (
                <div className="flex justify-center items-center py-20">
                    <Loader2 className="animate-spin text-blue-600" size={48} />
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
                        onClick={() => handleFiltrosChange({cidade: '', bairro: '', modalidade: '', tipo: '', ordenar_por: ''})}
                        className="mt-4 text-blue-600 hover:underline font-medium"
                    >
                        Limpar filtros
                    </button>
                </div>
            )}

            {!loading && meta.pages > 1 && (
                <div className="mt-12 flex justify-center gap-3">
                    <button 
                        onClick={() => mudarPagina(meta.page - 1)} 
                        disabled={meta.page === 1} 
                        className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50"
                    >
                        Anterior
                    </button>
                    <span className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border rounded-lg">
                        Página {meta.page} de {meta.pages}
                    </span>
                    <button 
                        onClick={() => mudarPagina(meta.page + 1)} 
                        disabled={meta.page === meta.pages} 
                        className="px-4 py-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50"
                    >
                        Próxima
                    </button>
                </div>
            )}
        </div>
    );
};

export default Home;