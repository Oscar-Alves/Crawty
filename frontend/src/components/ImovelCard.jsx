import { MapPin, BedDouble, Bath, Car, Ruler, TrendingDown, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

const FOTO_FALLBACK = 'https://placehold.co/600x400.png?text=Sem+Foto';

const formatMoney = (value) => {
    if (!value || value <= 0) return 'Sob Consulta';
    return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
};

const getBadgeColor = (modalidade) => {
    return modalidade === 'VENDA'
        ? 'bg-blue-600/95 text-white border-blue-500'
        : 'bg-emerald-600/95 text-white border-emerald-500';
};

const obterLabelQuartos = (suites) => {
    if (suites <= 0) return 'Quartos';
    const sufixo = suites > 1 ? 's' : '';
    return `${suites} suíte${sufixo}`;
};

const obterEnderecoCurto = (imovel) => {
    if (imovel.bairro && imovel.bairro !== 'Não Informado') {
        return `${imovel.bairro}, ${imovel.cidade}`;
    }
    return imovel.cidade;
};

const obterMetricasCard = (imovel) => {
    const fotoCapa = imovel.fotos?.length > 0 ? imovel.fotos[0] : FOTO_FALLBACK;
    const subtipo = imovel.extras?.subtipo;
    const tipoLower = (imovel.tipo || '').toLowerCase();
    const exibirSubtipo = Boolean(
        subtipo && subtipo !== 'Padrão' && subtipo.toLowerCase() !== tipoLower
    );
    const suites = imovel.extras?.suites || 0;
    const areaExibida = imovel.area_util || imovel.area_total || 0;
    const baixouPreco = Boolean(
        imovel.preco_anterior && imovel.preco > 0 && imovel.preco_anterior > imovel.preco
    );
    const percentualDesconto = baixouPreco
        ? Math.round(((imovel.preco_anterior - imovel.preco) / imovel.preco_anterior) * 100)
        : 0;
    const ehDestaque = Boolean(imovel.destaque);

    return {
        fotoCapa,
        subtipo,
        exibirSubtipo,
        suites,
        areaExibida,
        baixouPreco,
        percentualDesconto,
        ehDestaque,
    };
};

const ImovelCard = ({ imovel }) => {
    const {
        fotoCapa,
        subtipo,
        exibirSubtipo,
        suites,
        areaExibida,
        baixouPreco,
        percentualDesconto,
        ehDestaque,
    } = obterMetricasCard(imovel);

    const textoBadgeDesconto = percentualDesconto > 0 ? `-${percentualDesconto}%` : 'Baixou';
    const tituloQuartos = suites > 0 ? `${imovel.quartos} quartos (${suites} suíte)` : 'Quartos';
    const labelQuartos = obterLabelQuartos(suites);
    const labelModalidadePreco = imovel.modalidade === 'ALUGUEL' ? 'Aluguel' : 'Valor de Venda';

    return (
        <div
            className={`bg-white rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 overflow-hidden flex flex-col h-full group ${
                ehDestaque
                    ? 'border-2 border-amber-400 shadow-amber-100/60 ring-1 ring-amber-300/40'
                    : 'border border-gray-100'
            }`}
        >
            <div className="relative h-52 overflow-hidden bg-gray-100">
                <img
                    src={fotoCapa}
                    alt={imovel.titulo}
                    loading="lazy"
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    onError={(e) => {
                        e.target.src = FOTO_FALLBACK;
                    }}
                />
                <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
                    {ehDestaque && (
                        <span className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-extrabold bg-gradient-to-r from-amber-500 to-yellow-500 text-white shadow-md">
                            <Sparkles size={11} />
                            Destaque
                        </span>
                    )}
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

                <div className="absolute top-3 right-3 flex flex-col items-end gap-1">
                    {baixouPreco && (
                        <span className="flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-bold bg-rose-600 text-white shadow-sm">
                            <TrendingDown size={12} />
                            {textoBadgeDesconto}
                        </span>
                    )}
                    {imovel.ativo === false && (
                        <span className="px-2 py-0.5 rounded-md text-[10px] font-bold bg-amber-100 text-amber-800 border border-amber-300">
                            Inativo
                        </span>
                    )}
                </div>

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
                    <span className="truncate">{obterEnderecoCurto(imovel)}</span>
                </p>

                <div className="grid grid-cols-4 gap-1.5 mb-4 text-xs text-gray-600">
                    <div
                        className="flex flex-col items-center justify-center bg-gray-50 py-2 px-1 rounded-xl border border-gray-100"
                        title={tituloQuartos}
                    >
                        <span className="font-bold text-gray-900 flex items-center gap-1">
                            <BedDouble size={13} className="text-blue-600" /> {imovel.quartos}
                        </span>
                        <span className="text-[10px] text-gray-400 font-medium truncate">
                            {labelQuartos}
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
                            {labelModalidadePreco}
                        </p>
                        {baixouPreco && (
                            <p className="text-xs text-gray-400 line-through leading-none mb-0.5">
                                {formatMoney(imovel.preco_anterior)}
                            </p>
                        )}
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