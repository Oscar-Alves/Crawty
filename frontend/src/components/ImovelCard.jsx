import { MapPin, BedDouble, Bath, Ruler } from 'lucide-react';
import { Link } from 'react-router-dom';

const ImovelCard = ({ imovel }) => {
    const formatMoney = (value) => {
        if (!value) return "Sob Consulta";
        return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    };

    const getBadgeColor = (modalidade) => {
        return modalidade === 'VENDA' 
            ? 'bg-blue-100 text-blue-800 border-blue-200' 
            : 'bg-green-100 text-green-800 border-green-200';
    };

    const fotoCapa = imovel.fotos && imovel.fotos.length > 0 
        ? imovel.fotos[0] 
        : "https://via.placeholder.com/400x300?text=Sem+Foto";

    return (
        <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden border border-gray-100 flex flex-col h-full group">
            <div className="relative h-48 overflow-hidden">
                <img 
                    src={fotoCapa} 
                    alt={imovel.titulo} 
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                    onError={(e) => e.target.src = "https://via.placeholder.com/400x300?text=Erro+Foto"}
                />
                <div className="absolute top-3 left-3">
                    <span className={`px-2 py-1 rounded-md text-xs font-bold border ${getBadgeColor(imovel.modalidade)}`}>
                        {imovel.modalidade}
                    </span>
                </div>
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-3">
                    <p className="text-white text-xs font-medium truncate uppercase tracking-wider">{imovel.imobiliaria}</p>
                </div>
            </div>

            <div className="p-4 flex-1 flex flex-col">
                <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-1" title={imovel.titulo}>
                    {imovel.titulo}
                </h3>
                <p className="text-gray-500 text-sm mb-4 flex items-center gap-1 truncate">
                    <MapPin size={14} />
                    {imovel.bairro} - {imovel.cidade}
                </p>

                <div className="grid grid-cols-3 gap-2 mb-4 text-sm text-gray-600">
                    <div className="flex flex-col items-center bg-gray-50 p-2 rounded border border-gray-100">
                        <span className="font-bold text-gray-900 flex items-center gap-1"><BedDouble size={14}/> {imovel.quartos}</span>
                        <span className="text-[10px] uppercase text-gray-400 font-medium">Quartos</span>
                    </div>
                    <div className="flex flex-col items-center bg-gray-50 p-2 rounded border border-gray-100">
                        <span className="font-bold text-gray-900 flex items-center gap-1"><Bath size={14}/> {imovel.banheiros}</span>
                        <span className="text-[10px] uppercase text-gray-400 font-medium">Banho</span>
                    </div>
                    <div className="flex flex-col items-center bg-gray-50 p-2 rounded border border-gray-100">
                        <span className="font-bold text-gray-900 flex items-center gap-1"><Ruler size={14}/> {imovel.area_util || '-'}</span>
                        <span className="text-[10px] uppercase text-gray-400 font-medium">m²</span>
                    </div>
                </div>

                <div className="mt-auto pt-4 border-t border-gray-100 flex justify-between items-end">
                    <div>
                        <p className="text-xs text-gray-400 mb-0.5 font-medium">VALOR</p>
                        <p className="text-xl font-bold text-blue-600 leading-none">{formatMoney(imovel.preco)}</p>
                    </div>
                    <Link 
                        to={`/imovel/${imovel.id_unico}`}
                        className="bg-gray-900 hover:bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                        Detalhes
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default ImovelCard;