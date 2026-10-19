import { useState } from 'react';
import {
    Sparkles,
    X,
    Check,
    Flame,
    TrendingUp,
    ShieldAlert,
} from 'lucide-react';

const PLANOS_IMPULSIONAMENTO = [
    {
        id: '7dias',
        dias: 7,
        nome: '7 Dias (Bronze)',
        valor: 'R$ 19,90',
        beneficio: 'Ideal para giro rápido ou liquidação',
        popular: false,
    },
    {
        id: '15dias',
        dias: 15,
        nome: '15 Dias (Prata)',
        valor: 'R$ 34,90',
        beneficio: 'Mais escolhido: equilíbrio perfeito de exposição',
        popular: true,
    },
    {
        id: '30dias',
        dias: 30,
        nome: '30 Dias (Ouro)',
        valor: 'R$ 59,90',
        beneficio: 'Máximo alcance: 1 mês com prioridade no topo',
        popular: false,
    },
];

const formatarData = (dataIso) => {
    if (!dataIso) return '';
    try {
        return new Date(dataIso).toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    } catch {
        return '';
    }
};

const ModalImpulsionarImovel = ({
    imovel,
    onClose,
    onConfirmarImpulsionamento,
    onCancelarImpulsionamento,
    carregando,
}) => {
    const [planoSelecionado, setPlanoSelecionado] = useState('15dias');
    const [erro, setErro] = useState('');

    if (!imovel) return null;

    const ehDestaqueAtivo = Boolean(imovel.destaque);
    const planoAtual = PLANOS_IMPULSIONAMENTO.find((p) => p.id === planoSelecionado) || PLANOS_IMPULSIONAMENTO[1];

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErro('');
        try {
            await onConfirmarImpulsionamento(imovel.id_unico, {
                dias: planoAtual.dias,
                plano: planoAtual.id,
            });
            onClose();
        } catch (error) {
            setErro(error.message || 'Falha ao ativar impulsionamento.');
        }
    };

    const handleCancelar = async () => {
        setErro('');
        try {
            await onCancelarImpulsionamento(imovel.id_unico);
            onClose();
        } catch (error) {
            setErro(error.message || 'Falha ao cancelar impulsionamento.');
        }
    };

    return (
        <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-sm flex items-center justify-center p-3 sm:p-4 overflow-y-auto">
            <div className="bg-white rounded-3xl max-w-lg w-full border border-gray-100 shadow-2xl overflow-hidden my-6">
                <div className="bg-gradient-to-r from-amber-600 via-amber-500 to-yellow-500 p-6 text-white relative">
                    <button
                        type="button"
                        onClick={onClose}
                        className="absolute right-4 top-4 p-2 rounded-full bg-black/10 hover:bg-black/20 text-white transition-colors"
                    >
                        <X size={18} />
                    </button>
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-2xl bg-white/20 backdrop-blur-sm flex items-center justify-center text-white shrink-0">
                            <Sparkles size={24} />
                        </div>
                        <div>
                            <span className="text-[10px] font-extrabold uppercase tracking-widest px-2 py-0.5 rounded-full bg-white/20 text-yellow-100">
                                Vitrine Premium
                            </span>
                            <h2 className="text-xl font-extrabold mt-0.5">Impulsionar Imóvel</h2>
                        </div>
                    </div>
                </div>

                <div className="p-6 space-y-5">
                    <div className="p-3.5 bg-gray-50 border border-gray-200/80 rounded-2xl">
                        <p className="text-xs text-gray-400 font-bold uppercase tracking-wider">
                            Imóvel Selecionado
                        </p>
                        <h3 className="text-sm font-extrabold text-gray-900 truncate mt-0.5">
                            {imovel.titulo}
                        </h3>
                        <p className="text-xs text-gray-500">
                            Cód. {imovel.codigo_original} • {imovel.bairro}, {imovel.cidade}
                        </p>
                    </div>

                    {ehDestaqueAtivo && (
                        <div className="p-4 bg-amber-50 border border-amber-200 rounded-2xl flex items-start gap-3">
                            <Sparkles size={20} className="text-amber-600 shrink-0 mt-0.5" />
                            <div className="text-xs text-amber-900 flex-1">
                                <p className="font-bold">Este imóvel já está em Destaque!</p>
                                <p className="text-amber-800/90 mt-0.5">
                                    Vigente até: <strong>{formatarData(imovel.destaque_ate) || 'Ativo'}</strong>.
                                    Você pode estender o prazo selecionando um novo plano abaixo ou cancelar o destaque.
                                </p>
                            </div>
                        </div>
                    )}

                    {erro && (
                        <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                            <ShieldAlert size={16} className="shrink-0" />
                            <span>{erro}</span>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <span className="block text-xs font-bold uppercase tracking-wider text-gray-600 mb-2">
                                Escolha o período de impulsionamento:
                            </span>
                            <div className="grid grid-cols-1 gap-2.5">
                                {PLANOS_IMPULSIONAMENTO.map((plano) => {
                                    const selecionado = planoSelecionado === plano.id;
                                    return (
                                        <button
                                            key={plano.id}
                                            type="button"
                                            onClick={() => setPlanoSelecionado(plano.id)}
                                            className={`w-full text-left p-3.5 rounded-2xl border-2 transition-all flex items-center justify-between gap-3 ${
                                                selecionado
                                                    ? 'border-amber-500 bg-amber-50/60 shadow-sm'
                                                    : 'border-gray-200 hover:border-gray-300 bg-white'
                                            }`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <div
                                                    className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 ${
                                                        selecionado
                                                            ? 'border-amber-600 bg-amber-600 text-white'
                                                            : 'border-gray-300'
                                                    }`}
                                                >
                                                    {selecionado && <Check size={12} />}
                                                </div>
                                                <div>
                                                    <div className="flex items-center gap-2">
                                                        <span className="text-xs font-extrabold text-gray-900">
                                                            {plano.nome}
                                                        </span>
                                                        {plano.popular && (
                                                            <span className="px-2 py-0.5 rounded text-[10px] font-extrabold bg-amber-500 text-white">
                                                                Mais Popular
                                                            </span>
                                                        )}
                                                    </div>
                                                    <p className="text-[11px] text-gray-500 mt-0.5">
                                                        {plano.beneficio}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="text-right shrink-0">
                                                <span className="text-sm font-extrabold text-amber-700">
                                                    {plano.valor}
                                                </span>
                                            </div>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>

                        <div className="p-3.5 bg-gray-50 rounded-2xl border border-gray-100 space-y-2">
                            <p className="text-[11px] font-bold uppercase tracking-wider text-gray-500">
                                Benefícios Garantidos:
                            </p>
                            <ul className="text-xs text-gray-600 space-y-1.5">
                                <li className="flex items-center gap-2">
                                    <TrendingUp size={14} className="text-amber-600 shrink-0" />
                                    <span><strong>Topo dos Resultados:</strong> Exibição prioritária na busca padrão por relevância.</span>
                                </li>
                                <li className="flex items-center gap-2">
                                    <Sparkles size={14} className="text-amber-600 shrink-0" />
                                    <span><strong>Selo Dourado:</strong> Destaque visual nos cards e detalhes do imóvel.</span>
                                </li>
                                <li className="flex items-center gap-2">
                                    <Flame size={14} className="text-amber-600 shrink-0" />
                                    <span><strong>Prioridade no Modo Match:</strong> Aparece primeiro na pilha de swipes dos usuários.</span>
                                </li>
                            </ul>
                        </div>

                        <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5">
                            {ehDestaqueAtivo ? (
                                <button
                                    type="button"
                                    onClick={handleCancelar}
                                    disabled={carregando}
                                    className="px-4 py-2.5 rounded-xl border border-rose-200 text-rose-600 hover:bg-rose-50 text-xs font-bold transition-colors disabled:opacity-50 text-center"
                                >
                                    Cancelar Destaque
                                </button>
                            ) : (
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="px-4 py-2.5 rounded-xl border border-gray-200 text-gray-600 hover:bg-gray-50 text-xs font-bold transition-colors text-center"
                                >
                                    Voltar
                                </button>
                            )}

                            <button
                                type="submit"
                                disabled={carregando}
                                className="flex-1 inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-white font-extrabold text-xs sm:text-sm shadow-md hover:shadow-lg transition-all disabled:opacity-50"
                            >
                                <Sparkles size={16} />
                                <span>
                                    {(() => {
                                        if (carregando) return 'Ativando...';
                                        if (ehDestaqueAtivo) return `Renovar por ${planoAtual.dias} dias`;
                                        return `Ativar Destaque (${planoAtual.valor})`;
                                    })()}
                                </span>
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    );
};

export default ModalImpulsionarImovel;

