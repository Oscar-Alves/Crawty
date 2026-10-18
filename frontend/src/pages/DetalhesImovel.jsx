import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getImovelDetalhes } from '../services/api';
import {
    MapPin,
    BedDouble,
    Bath,
    Car,
    Ruler,
    ArrowLeft,
    Share2,
    Calendar,
    Sparkles,
    Check,
} from 'lucide-react';

const DetalhesImovel = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [imovel, setImovel] = useState(null);
    const [loading, setLoading] = useState(true);
    const [fotoAtiva, setFotoAtiva] = useState(0);
    const [copiado, setCopiado] = useState(false);

    useEffect(() => {
        getImovelDetalhes(id)
            .then((data) => setImovel(data))
            .catch((err) => console.error(err))
            .finally(() => setLoading(false));
    }, [id]);

    const compartilhar = () => {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(window.location.href);
            setCopiado(true);
            setTimeout(() => setCopiado(false), 2000);
        }
    };

    if (loading)
        return (
            <div className="h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    if (!imovel) return <div className="text-center py-20">Imóvel não encontrado.</div>;

    const logradouro = imovel.extras?.logradouro;
    const numero = imovel.extras?.numero;
    const subtipo = imovel.extras?.subtipo;
    const suites = imovel.extras?.suites || 0;
    const salas = imovel.extras?.salas || 0;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
            <button
                onClick={() => navigate(-1)}
                className="flex items-center text-gray-500 hover:text-blue-600 mb-6 transition-colors font-medium text-sm"
            >
                <ArrowLeft size={18} className="mr-1.5" /> Voltar para a busca
            </button>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Coluna da Esquerda: Fotos e Infos */}
                <div className="lg:col-span-2">
                    <div className="bg-gray-100 rounded-2xl overflow-hidden h-[380px] md:h-[500px] mb-4 relative group">
                        <img
                            src={
                                imovel.fotos?.[fotoAtiva] ||
                                'https://placehold.co/800x600?text=Sem+Foto'
                            }
                            className="w-full h-full object-contain bg-black"
                            alt="Foto Principal"
                        />
                        {imovel.fotos?.length > 0 && (
                            <div className="absolute bottom-4 right-4 bg-black/70 text-white px-3 py-1 rounded-full text-xs backdrop-blur-sm">
                                {fotoAtiva + 1} / {imovel.fotos.length}
                            </div>
                        )}
                    </div>

                    {imovel.fotos?.length > 1 && (
                        <div className="flex gap-2 overflow-x-auto pb-2 mb-8 custom-scrollbar">
                            {imovel.fotos.map((foto, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => setFotoAtiva(idx)}
                                    className={`shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition-all ${
                                        fotoAtiva === idx
                                            ? 'border-blue-600 opacity-100'
                                            : 'border-transparent opacity-60 hover:opacity-100'
                                    }`}
                                >
                                    <img src={foto} className="w-full h-full object-cover" alt="" />
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Títulos e Detalhes */}
                    <div className="bg-white rounded-2xl border border-gray-100 p-6 md:p-8 shadow-sm mb-8">
                        <div className="flex flex-wrap justify-between items-start gap-4 mb-4">
                            <div>
                                <div className="flex flex-wrap gap-2 items-center mb-2">
                                    <span className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs font-bold border border-blue-100">
                                        {imovel.tipo}
                                    </span>
                                    {subtipo && subtipo !== 'Padrão' && subtipo !== imovel.tipo && (
                                        <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-xs font-semibold">
                                            {subtipo}
                                        </span>
                                    )}
                                    {imovel.ativo === false && (
                                        <span className="bg-amber-100 text-amber-800 px-3 py-1 rounded-full text-xs font-bold border border-amber-200">
                                            Descontinuado
                                        </span>
                                    )}
                                </div>
                                <h1 className="text-2xl md:text-3xl font-bold text-gray-900 mb-2">
                                    {imovel.titulo}
                                </h1>
                                <p className="text-gray-500 flex items-center gap-2 text-sm">
                                    <MapPin size={18} className="text-blue-600 shrink-0" />
                                    <span>
                                        {logradouro ? `${logradouro}${numero ? `, ${numero}` : ''} - ` : ''}
                                        {imovel.bairro && imovel.bairro !== 'Não Informado'
                                            ? `${imovel.bairro}, `
                                            : ''}
                                        {imovel.cidade}
                                    </span>
                                </p>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 py-6 border-y border-gray-100 mb-6">
                            <div className="text-center p-3 bg-gray-50 rounded-xl">
                                <BedDouble className="mx-auto mb-1.5 text-blue-600" size={22} />
                                <div className="font-bold text-lg text-gray-900">
                                    {imovel.quartos}
                                </div>
                                <div className="text-[11px] text-gray-500 uppercase font-medium">
                                    Quartos
                                </div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 rounded-xl">
                                <Sparkles className="mx-auto mb-1.5 text-blue-600" size={22} />
                                <div className="font-bold text-lg text-gray-900">{suites}</div>
                                <div className="text-[11px] text-gray-500 uppercase font-medium">
                                    Suítes
                                </div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 rounded-xl">
                                <Bath className="mx-auto mb-1.5 text-blue-600" size={22} />
                                <div className="font-bold text-lg text-gray-900">
                                    {imovel.banheiros}
                                </div>
                                <div className="text-[11px] text-gray-500 uppercase font-medium">
                                    Banheiros
                                </div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 rounded-xl">
                                <Car className="mx-auto mb-1.5 text-blue-600" size={22} />
                                <div className="font-bold text-lg text-gray-900">
                                    {imovel.vagas}
                                </div>
                                <div className="text-[11px] text-gray-500 uppercase font-medium">
                                    Vagas
                                </div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 rounded-xl">
                                <Ruler className="mx-auto mb-1.5 text-blue-600" size={22} />
                                <div className="font-bold text-lg text-gray-900">
                                    {imovel.area_util ? `${imovel.area_util} m²` : '-'}
                                </div>
                                <div className="text-[11px] text-gray-500 uppercase font-medium">
                                    Área Útil
                                </div>
                            </div>
                            <div className="text-center p-3 bg-gray-50 rounded-xl">
                                <Ruler className="mx-auto mb-1.5 text-blue-600" size={22} />
                                <div className="font-bold text-lg text-gray-900">
                                    {imovel.area_total ? `${imovel.area_total} m²` : '-'}
                                </div>
                                <div className="text-[11px] text-gray-500 uppercase font-medium">
                                    Área Terreno
                                </div>
                            </div>
                        </div>

                        <h3 className="text-base font-bold text-gray-900 mb-3">
                            Diferenciais e Informações Adicionais
                        </h3>
                        <div className="flex flex-wrap gap-2 mb-6">
                            {salas > 0 && (
                                <span className="bg-blue-50 text-blue-700 px-3 py-1.5 rounded-lg text-xs font-semibold border border-blue-100">
                                    {salas} Sala{salas > 1 ? 's' : ''}
                                </span>
                            )}
                            {imovel.extras?.atributos ? (
                                imovel.extras.atributos.split(',').map((attr, i) => (
                                    <span
                                        key={i}
                                        className="bg-emerald-50 text-emerald-700 px-3 py-1.5 rounded-lg text-xs font-semibold border border-emerald-100"
                                    >
                                        {attr.trim()}
                                    </span>
                                ))
                            ) : (
                                salas === 0 && (
                                    <p className="text-gray-400 italic text-sm">
                                        Nenhum atributo adicional informado.
                                    </p>
                                )
                            )}
                        </div>

                        {imovel.last_updated && (
                            <div className="text-xs text-gray-400 flex items-center gap-1.5 mt-8">
                                <Calendar size={13} /> Atualizado em:{' '}
                                {new Date(imovel.last_updated).toLocaleDateString('pt-BR')}
                            </div>
                        )}
                    </div>
                </div>

                {/* Coluna da Direita: Card Flutuante */}
                <div className="lg:col-span-1">
                    <div className="sticky top-24 space-y-4">
                        <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-lg">
                            <p className="text-xs text-gray-500 mb-1 font-bold uppercase tracking-wider">
                                Valor de {imovel.modalidade}
                            </p>
                            <p className="text-3xl md:text-4xl font-extrabold text-blue-600 mb-6 tracking-tight">
                                {imovel.preco
                                    ? imovel.preco.toLocaleString('pt-BR', {
                                          style: 'currency',
                                          currency: 'BRL',
                                      })
                                    : 'Sob Consulta'}
                            </p>

                            {imovel.ativo === false ? (
                                <div className="block w-full bg-amber-50 text-amber-800 text-center font-medium py-3 rounded-xl mb-3 border border-amber-200 text-sm">
                                    ⚠️ Imóvel retirado do ar pela imobiliária
                                </div>
                            ) : (
                                <a
                                    href={imovel.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="block w-full bg-emerald-600 hover:bg-emerald-700 text-white text-center font-bold py-4 rounded-xl transition-all shadow-md hover:shadow-lg mb-3"
                                >
                                    Ver no site da {imovel.imobiliaria}
                                </a>
                            )}

                            <button
                                onClick={compartilhar}
                                className="w-full bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 text-center font-medium py-3 rounded-xl transition-colors flex items-center justify-center gap-2 text-sm"
                            >
                                {copiado ? (
                                    <>
                                        <Check size={17} className="text-emerald-600" /> Link copiado!
                                    </>
                                ) : (
                                    <>
                                        <Share2 size={17} /> Compartilhar
                                    </>
                                )}
                            </button>
                        </div>

                        <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                            <p className="text-sm text-blue-800 font-medium">
                                💡 <strong>Dica:</strong> Ao entrar em contato com a{' '}
                                <strong>{imovel.imobiliaria}</strong>, informe o código{' '}
                                <strong>{imovel.codigo_original}</strong>.
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DetalhesImovel;