import { MapPin, BedDouble, Bath, Car, Ruler, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

const ImovelCard = ({ imovel }) => {
    const formatMoney = (value) => {
        if (!value || value <= 0) return 'Sob Consulta';
        return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
    };

    const getBadgeColor = (modalidade) => {
        return modalidade === 'VENDA'
            ? 'bg-blue-600/95 text-white border-blue-500'
            : 'bg-emerald-600/95 text-white border-emerald-500';
    };

    const fotoCapa =
        imovel.fotos && imovel.fotos.length > 0
            ? imovel.fotos[0]
            : 'https://placehold.co/600x400.png?text=Sem+Foto';

    const subtipo = imovel.extras?.subtipo;
    const exibirSubtipo =
        subtipo && subtipo !== 'Padrão' && subtipo.toLowerCase() !== (imovel.tipo || '').toLowerCase();

    const suites = imovel.extras?.suites || 0;
    const areaExibida = imovel.area_util || imovel.area_total || 0;

    return (
        <div className="bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden border border-gray-100 flex flex-col h-full group">
            <div className="relative h-52 overflow-hidden bg-gray-100">
                <img
                    src={fotoCapa}
                    alt={imovel.titulo}
                    loading="lazy"
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    onError={(e) => {
                        e.target.src = 'https://placehold.co/600x400.png?text=Sem+Foto';
                    }}
                />
                <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
                    <span
                        className={`px-2.5 py-1 rounded-lg text-[11px] font-bold tracking-wide shadow-sm backdrop-blur-sm border ${getBadgeColor(
                            imovel.modalidade
                        )}`}
                    >
                        {imovel.modalidade === 'VENDA' ? 'VENDA' : 'ALUGUEL'}
                    </span>
                    <span className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-white/95 text-gray-800 shadow-sm backdrop-blur-sm">
                        {imovel.tipo}
                        {exibirSubtipo ? ` • ${subtipo}` : ''}
                    </span>
                </div>

                {imovel.ativo === false && (
                    <div className="absolute top-3 right-3">
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                            Inativo
                        </span>
                    </div>
                )}

                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-3 pt-8 flex items-end justify-between gap-2">
                    <p className="text-white text-xs font-semibold truncate uppercase tracking-wider">
                        {imovel.imobiliaria}
                    </p>
                    {imovel.codigo_original && (
                        <span className="text-[10px] text-gray-200 bg-black/40 px-2 py-0.5 rounded font-mono shrink-0">
                            Cód. {imovel.codigo_original}
                        </span>
                    )}
                </div>
            </div>

            <div className="p-4 flex-1 flex flex-col">
                <h3
                    className="text-base font-bold text-gray-900 mb-1 line-clamp-1 group-hover:text-blue-600 transition-colors"
                    title={imovel.titulo}
                >
                    {imovel.titulo}
                </h3>
                <p className="text-gray-500 text-xs mb-4 flex items-center gap-1.5 truncate">
                    <MapPin size={14} className="text-blue-600 shrink-0" />
                    <span className="truncate">
                        {imovel.bairro && imovel.bairro !== 'Não Informado'
                            ? `${imovel.bairro}, ${imovel.cidade}`
                            : imovel.cidade}
                    </span>
                </p>

                <div className="grid grid-cols-4 gap-1.5 mb-4 text-xs text-gray-600">
                    <div
                        className="flex flex-col items-center justify-center bg-gray-50 py-2 px-1 rounded-xl border border-gray-100"
                        title={suites > 0 ? `${imovel.quartos} quartos (${suites} suíte)` : 'Quartos'}
                    >
                        <span className="font-bold text-gray-900 flex items-center gap-1">
                            <BedDouble size={13} className="text-blue-600" /> {imovel.quartos}
                        </span>
                        <span className="text-[10px] text-gray-400 font-medium truncate">
                            {suites > 0 ? `${suites} suíte${suites > 1 ? 's' : ''}` : 'Quartos'}
                        </span>
                    </div>

                    <div className="flex flex-col items-center justify-center bg-gray-50 py-2 px-1 rounded-xl border border-gray-100">
                        <span className="font-bold text-gray-900 flex items-center gap-1">
                            <Bath size={13} className="text-blue-600" /> {imovel.banheiros}
                        </span>
                        <span className="text-[10px] text-gray-400 font-medium">Banho</span>
                    </div>

                    <div className="flex flex-col items-center justify-center bg-gray-50 py-2 px-1 rounded-xl border border-gray-100">
                        <span className="font-bold text-gray-900 flex items-center gap-1">
                            <Car size={13} className="text-blue-600" /> {imovel.vagas || 0}
                        </span>
                        <span className="text-[10px] text-gray-400 font-medium">Vagas</span>
                    </div>

                    <div className="flex flex-col items-center justify-center bg-gray-50 py-2 px-1 rounded-xl border border-gray-100">
                        <span className="font-bold text-gray-900 flex items-center gap-1">
                            <Ruler size={13} className="text-blue-600" />{' '}
                            {areaExibida > 0 ? Math.round(areaExibida) : '-'}
                        </span>
                        <span className="text-[10px] text-gray-400 font-medium">m²</span>
                    </div>
                </div>

                <div className="mt-auto pt-3.5 border-t border-gray-100 flex justify-between items-end gap-2">
                    <div>
                        <p className="text-[10px] text-gray-400 mb-0.5 font-bold uppercase tracking-wider">
                            {imovel.modalidade === 'ALUGUEL' ? 'Aluguel' : 'Valor de Venda'}
                        </p>
                        <p className="text-lg font-extrabold text-blue-600 leading-none">
                            {formatMoney(imovel.preco)}
                        </p>
                    </div>
                    <Link
                        to={`/imovel/${imovel.id_unico}`}
                        className="bg-gray-900 hover:bg-blue-600 text-white px-4 py-2 rounded-xl text-xs font-semibold transition-colors shrink-0"
                    >
                        Ver detalhes
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default ImovelCard;