import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getImovelDetalhes } from '../services/api';
import { MapPin, BedDouble, Bath, Car, Ruler, ArrowLeft, Share2, Calendar } from 'lucide-react';

const DetalhesImovel = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [imovel, setImovel] = useState(null);
    const [loading, setLoading] = useState(true);
    const [fotoAtiva, setFotoAtiva] = useState(0);

    useEffect(() => {
        getImovelDetalhes(id)
            .then(data => setImovel(data))
            .catch(err => console.error(err))
            .finally(() => setLoading(false));
    }, [id]);

    if (loading) return <div className="h-screen flex items-center justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div></div>;
    if (!imovel) return <div className="text-center py-20">Imóvel não encontrado.</div>;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
            {/* Botão Voltar */}
            <button onClick={() => navigate(-1)} className="flex items-center text-gray-500 hover:text-blue-600 mb-6 transition-colors">
                <ArrowLeft size={20} className="mr-1"/> Voltar para a lista
            </button>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Coluna da Esquerda: Fotos e Infos */}
                <div className="lg:col-span-2">
                    {/* Galeria Principal */}
                    <div className="bg-gray-100 rounded-2xl overflow-hidden h-[400px] md:h-[500px] mb-4 relative group">
                        <img 
                            src={imovel.fotos[fotoAtiva] || "https://via.placeholder.com/800x600?text=Sem+Foto"} 
                            className="w-full h-full object-contain bg-black"
                            alt="Foto Principal"
                        />
                        <div className="absolute bottom-4 right-4 bg-black/70 text-white px-3 py-1 rounded-full text-xs backdrop-blur-sm">
                            {fotoAtiva + 1} / {imovel.fotos.length}
                        </div>
                    </div>
                    
                    {/* Miniaturas */}
                    <div className="flex gap-2 overflow-x-auto pb-2 mb-8 custom-scrollbar">
                        {imovel.fotos.map((foto, idx) => (
                            <button 
                                key={idx}
                                onClick={() => setFotoAtiva(idx)}
                                className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all ${fotoAtiva === idx ? 'border-blue-600 opacity-100' : 'border-transparent opacity-60 hover:opacity-100'}`}
                            >
                                <img src={foto} className="w-full h-full object-cover" />
                            </button>
                        ))}
                    </div>

                    {/* Títulos e Detalhes */}
                    <div className="bg-white rounded-2xl border border-gray-100 p-8 shadow-sm mb-8">
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">{imovel.titulo}</h1>
                                <p className="text-gray-500 flex items-center gap-2">
                                    <MapPin size={18} className="text-blue-600"/> 
                                    {imovel.logradouro ? `${imovel.logradouro}, ` : ''}{imovel.bairro} - {imovel.cidade}
                                </p>
                            </div>
                            <span className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-bold border border-blue-100">
                                {imovel.tipo}
                            </span>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 py-6 border-y border-gray-100 mb-6">
                            <div className="text-center p-3 bg-gray-50 rounded-xl">
                                <BedDouble className="mx-auto mb-2 text-gray-400" size={24}/>
                                <div className="font-bold text-lg text-gray-900">{imovel.quartos}</div>
                                <div className="text-xs text-gray-500 uppercase">Quartos</div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 rounded-xl">
                                <Bath className="mx-auto mb-2 text-gray-400" size={24}/>
                                <div className="font-bold text-lg text-gray-900">{imovel.banheiros}</div>
                                <div className="text-xs text-gray-500 uppercase">Banheiros</div>
                            </div>
                             <div className="text-center p-3 bg-gray-50 rounded-xl">
                                <Car className="mx-auto mb-2 text-gray-400" size={24}/>
                                <div className="font-bold text-lg text-gray-900">{imovel.vagas}</div>
                                <div className="text-xs text-gray-500 uppercase">Vagas</div>
                            </div>
                             <div className="text-center p-3 bg-gray-50 rounded-xl">
                                <Ruler className="mx-auto mb-2 text-gray-400" size={24}/>
                                <div className="font-bold text-lg text-gray-900">{imovel.area_util || '-'}</div>
                                <div className="text-xs text-gray-500 uppercase">Área Útil</div>
                            </div>
                        </div>

                        <h3 className="text-lg font-bold text-gray-900 mb-4">Diferenciais</h3>
                        <div className="flex flex-wrap gap-2 mb-6">
                            {imovel.extras.atributos ? imovel.extras.atributos.split(',').map((attr, i) => (
                                <span key={i} className="bg-green-50 text-green-700 px-3 py-1.5 rounded-lg text-sm font-medium border border-green-100">
                                    {attr.trim()}
                                </span>
                            )) : <p className="text-gray-400 italic">Nenhum atributo informado.</p>}
                        </div>
                        
                        <div className="text-xs text-gray-400 flex items-center gap-1 mt-8">
                            <Calendar size={12} /> Atualizado em: {new Date(imovel.last_updated).toLocaleDateString()}
                        </div>
                    </div>
                </div>

                {/* Coluna da Direita: Card Flutuante */}
                <div className="lg:col-span-1">
                    <div className="sticky top-24 space-y-4">
                        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-lg">
                            <p className="text-sm text-gray-500 mb-1 font-medium uppercase tracking-wide">Valor de {imovel.modalidade}</p>
                            <p className="text-4xl font-extrabold text-blue-600 mb-6 tracking-tight">
                                {imovel.preco ? imovel.preco.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) : "Sob Consulta"}
                            </p>
                            
                            <a 
                                href={imovel.link} 
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block w-full bg-green-600 hover:bg-green-700 text-white text-center font-bold py-4 rounded-xl transition-all shadow-md hover:shadow-lg mb-3 transform hover:-translate-y-0.5"
                            >
                                Ver no site da {imovel.imobiliaria}
                            </a>
                            
                            <button className="block w-full bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 text-center font-medium py-3 rounded-xl transition-colors flex items-center justify-center gap-2">
                                <Share2 size={18}/> Compartilhar
                            </button>
                        </div>

                        <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                            <p className="text-sm text-blue-800 font-medium">
                                💡 <strong>Dica:</strong> Ao entrar em contato, diga que viu o imóvel pelo código <strong>{imovel.codigo_original}</strong>.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DetalhesImovel;