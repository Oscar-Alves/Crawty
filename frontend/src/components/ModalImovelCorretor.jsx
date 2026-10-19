import { useState, useEffect } from 'react';
import {
    X,
    Plus,
    Trash2,
    Save,
    Image as ImageIcon,
    MapPin,
    Home,
    Phone,
    AlertCircle,
} from 'lucide-react';

const TIPOS_IMOVEL = ['Casa', 'Apartamento', 'Terreno', 'Comercial', 'Rural', 'Kitnet'];

const SUBTIPOS_SUGERIDOS = [
    'Padrão',
    'Sobrado',
    'Cobertura',
    'Duplex',
    'Triplex',
    'Gemina',
    'Condomínio Fechado',
    'Lote',
    'Chácara',
    'Sítio',
    'Fazenda',
    'Loja',
    'Sala',
    'Galpão',
    'Prédio',
    'Loft',
];

const criarEstadoInicialFormulario = (imovel, corretor) => {
    if (!imovel) {
        return {
            codigo_original: '',
            titulo: '',
            descricao: '',
            modalidade: 'VENDA',
            tipo: 'Casa',
            subtipo: 'Padrão',
            preco: '',
            cidade: 'São João del Rei',
            bairro: '',
            logradouro: '',
            numero: '',
            quartos: 0,
            suites: 0,
            banheiros: 0,
            vagas: 0,
            salas: 0,
            area_util: '',
            area_total: '',
            atributos: '',
            fotos: [],
            link_externo: '',
            whatsapp_contato: corretor?.whatsapp || '',
            telefone_contato: corretor?.telefone || '',
            ativo: true,
        };
    }

    const linkAtual = imovel.link || '';
    const ehLinkExterno =
        linkAtual.startsWith('http') && !linkAtual.includes('wa.me/');

    return {
        codigo_original: imovel.codigo_original || '',
        titulo: imovel.titulo || '',
        descricao: imovel.descricao || '',
        modalidade: imovel.modalidade || 'VENDA',
        tipo: imovel.tipo || 'Casa',
        subtipo: imovel.extras?.subtipo || 'Padrão',
        preco: imovel.preco ?? '',
        cidade: imovel.cidade || 'São João del Rei',
        bairro: imovel.bairro || '',
        logradouro: imovel.extras?.logradouro || '',
        numero: imovel.extras?.numero || '',
        quartos: imovel.quartos ?? 0,
        suites: imovel.extras?.suites ?? 0,
        banheiros: imovel.banheiros ?? 0,
        vagas: imovel.vagas ?? 0,
        salas: imovel.extras?.salas ?? 0,
        area_util: imovel.area_util || '',
        area_total: imovel.area_total || '',
        atributos: imovel.extras?.atributos || '',
        fotos: Array.isArray(imovel.fotos) ? [...imovel.fotos] : [],
        link_externo: ehLinkExterno ? linkAtual : '',
        whatsapp_contato: imovel.contato_corretor?.whatsapp || corretor?.whatsapp || '',
        telefone_contato: imovel.contato_corretor?.telefone || corretor?.telefone || '',
        ativo: imovel.ativo !== false,
    };
};

const SecaoGaleriaFotosForm = ({ fotos, onAdicionarUrls, onRemoverFoto }) => {
    const [novaUrl, setNovaUrl] = useState('');

    const handleInserir = () => {
        if (!novaUrl.trim()) return;
        const partes = novaUrl
            .split(/[\n,]+/)
            .map((u) => u.trim())
            .filter((u) => u.startsWith('http://') || u.startsWith('https://'));
        if (partes.length > 0) {
            onAdicionarUrls(partes);
            setNovaUrl('');
        }
    };

    return (
        <div className="pt-4 border-t border-gray-100">
            <label
                htmlFor="modal-imovel-nova-foto"
                className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-gray-700 mb-2"
            >
                <ImageIcon size={15} className="text-blue-600" />
                <span>Fotos do Imóvel ({fotos.length})</span>
            </label>

            <div className="flex gap-2">
                <input
                    id="modal-imovel-nova-foto"
                    type="url"
                    placeholder="Cole a URL da imagem (https://...) e clique em Adicionar"
                    value={novaUrl}
                    onChange={(e) => setNovaUrl(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            handleInserir();
                        }
                    }}
                    className="flex-1 rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-sm text-gray-900 focus:bg-white focus:border-blue-600 focus:outline-none"
                />
                <button
                    type="button"
                    onClick={handleInserir}
                    className="inline-flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 font-bold text-xs sm:text-sm transition-colors shrink-0"
                >
                    <Plus size={16} />
                    <span>Adicionar Foto</span>
                </button>
            </div>

            {fotos.length > 0 && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
                    {fotos.map((url) => (
                        <div
                            key={url}
                            className="relative group rounded-xl overflow-hidden border border-gray-200 bg-gray-100 h-24"
                        >
                            <img
                                src={url}
                                alt="Preview do imóvel"
                                className="w-full h-full object-cover"
                            />
                            <button
                                type="button"
                                onClick={() => onRemoverFoto(url)}
                                title="Remover foto"
                                className="absolute top-1.5 right-1.5 p-1.5 rounded-lg bg-black/70 text-white hover:bg-rose-600 transition-colors"
                            >
                                <Trash2 size={13} />
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

const ModalImovelCorretor = ({
    aberto,
    imovelEdicao,
    corretor,
    salvando,
    onFechar,
    onSalvar,
}) => {
    const [form, setForm] = useState(() => criarEstadoInicialFormulario(imovelEdicao, corretor));
    const [erroValidacao, setErroValidacao] = useState('');

    useEffect(() => {
        if (aberto) {
            setForm(criarEstadoInicialFormulario(imovelEdicao, corretor));
            setErroValidacao('');
        }
    }, [aberto, imovelEdicao, corretor]);

    if (!aberto) return null;

    const atualizarCampo = (campo, valor) => {
        setForm((prev) => ({ ...prev, [campo]: valor }));
    };

    const handleAdicionarFotos = (novasUrls) => {
        setForm((prev) => {
            const conjunto = new Set([...prev.fotos, ...novasUrls]);
            return { ...prev, fotos: Array.from(conjunto) };
        });
    };

    const handleRemoverFoto = (urlAlvo) => {
        setForm((prev) => ({
            ...prev,
            fotos: prev.fotos.filter((u) => u !== urlAlvo),
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        setErroValidacao('');

        if (!form.titulo.trim() || form.titulo.trim().length < 3) {
            setErroValidacao('Informe um título descritivo para o imóvel (mínimo 3 caracteres).');
            return;
        }
        if (form.preco === '' || Number(form.preco) <= 0) {
            setErroValidacao('Informe um valor válido maior que zero para o imóvel.');
            return;
        }
        if (!form.bairro.trim()) {
            setErroValidacao('Informe o bairro onde o imóvel está localizado.');
            return;
        }

        const payload = {
            ...form,
            preco: Number(form.preco),
            quartos: Number(form.quartos || 0),
            suites: Number(form.suites || 0),
            banheiros: Number(form.banheiros || 0),
            vagas: Number(form.vagas || 0),
            salas: Number(form.salas || 0),
            area_util: Number(form.area_util || 0),
            area_total: Number(form.area_total || 0),
        };

        onSalvar(payload);
    };

    const inputClass =
        'w-full rounded-xl border border-gray-200 bg-gray-50 px-3.5 py-2.5 text-sm text-gray-900 focus:bg-white focus:border-blue-600 focus:outline-none';
    const labelClass = 'block text-xs font-bold uppercase tracking-wider text-gray-600 mb-1.5';

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-3 sm:p-6 overflow-y-auto">
            <div className="bg-white rounded-3xl border border-gray-200 shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden">
                {/* Cabeçalho do Modal */}
                <div className="px-6 py-4 bg-gradient-to-r from-slate-900 to-blue-950 text-white flex items-center justify-between shrink-0">
                    <div>
                        <h2 className="text-lg font-extrabold">
                            {imovelEdicao ? 'Editar Imóvel / Alterar Preço' : 'Cadastrar Novo Imóvel'}
                        </h2>
                        <p className="text-xs text-blue-200">
                            {imovelEdicao
                                ? `Editando código ${imovelEdicao.codigo_original} • Alterações de preço geram histórico automático`
                                : 'Preencha os dados abaixo para publicar seu imóvel na vitrine e no Modo Match'}
                        </p>
                    </div>
                    <button
                        type="button"
                        onClick={onFechar}
                        aria-label="Fechar janela"
                        className="p-2 rounded-xl text-white/75 hover:text-white hover:bg-white/10 transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Corpo do Formulário */}
                <form onSubmit={handleSubmit} className="p-6 overflow-y-auto space-y-6 flex-1">
                    {erroValidacao && (
                        <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 flex items-center gap-2 text-rose-700 text-xs sm:text-sm font-semibold">
                            <AlertCircle size={18} className="shrink-0" />
                            <span>{erroValidacao}</span>
                        </div>
                    )}

                    {/* 1. Dados Principais e Preço */}
                    <div>
                        <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-blue-600 mb-3">
                            <Home size={15} />
                            <span>1. Informações Principais & Valor</span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-12 gap-4">
                            <div className="sm:col-span-8">
                                <label htmlFor="modal-imovel-titulo" className={labelClass}>
                                    Título do Anúncio *
                                </label>
                                <input
                                    id="modal-imovel-titulo"
                                    type="text"
                                    placeholder="Ex: Casa linear com 3 quartos e área gourmet no Tejuco"
                                    value={form.titulo}
                                    onChange={(e) => atualizarCampo('titulo', e.target.value)}
                                    className={inputClass}
                                />
                            </div>

                            <div className="sm:col-span-4">
                                <label htmlFor="modal-imovel-codigo" className={labelClass}>
                                    Código Interno (Opcional)
                                </label>
                                <input
                                    id="modal-imovel-codigo"
                                    type="text"
                                    placeholder="Auto-gerado se vazio"
                                    value={form.codigo_original}
                                    disabled={Boolean(imovelEdicao)}
                                    onChange={(e) => atualizarCampo('codigo_original', e.target.value)}
                                    className={`${inputClass} disabled:opacity-60`}
                                />
                            </div>

                            <div className="sm:col-span-3">
                                <label htmlFor="modal-imovel-modalidade" className={labelClass}>
                                    Finalidade *
                                </label>
                                <select
                                    id="modal-imovel-modalidade"
                                    value={form.modalidade}
                                    onChange={(e) => atualizarCampo('modalidade', e.target.value)}
                                    className={inputClass}
                                >
                                    <option value="VENDA">Venda</option>
                                    <option value="ALUGUEL">Aluguel</option>
                                </select>
                            </div>

                            <div className="sm:col-span-3">
                                <label htmlFor="modal-imovel-tipo" className={labelClass}>
                                    Tipo *
                                </label>
                                <select
                                    id="modal-imovel-tipo"
                                    value={form.tipo}
                                    onChange={(e) => atualizarCampo('tipo', e.target.value)}
                                    className={inputClass}
                                >
                                    {TIPOS_IMOVEL.map((t) => (
                                        <option key={t} value={t}>
                                            {t}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="sm:col-span-3">
                                <label htmlFor="modal-imovel-subtipo" className={labelClass}>
                                    Subtipo
                                </label>
                                <select
                                    id="modal-imovel-subtipo"
                                    value={form.subtipo}
                                    onChange={(e) => atualizarCampo('subtipo', e.target.value)}
                                    className={inputClass}
                                >
                                    {SUBTIPOS_SUGERIDOS.map((st) => (
                                        <option key={st} value={st}>
                                            {st}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="sm:col-span-3">
                                <label htmlFor="modal-imovel-preco" className={labelClass}>
                                    Valor (R$) *
                                </label>
                                <input
                                    id="modal-imovel-preco"
                                    type="number"
                                    min="0"
                                    step="100"
                                    placeholder="Ex: 450000"
                                    value={form.preco}
                                    onChange={(e) => atualizarCampo('preco', e.target.value)}
                                    className={`${inputClass} font-bold text-blue-700`}
                                />
                            </div>
                        </div>
                    </div>

                    {/* 2. Localização */}
                    <div className="pt-4 border-t border-gray-100">
                        <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-blue-600 mb-3">
                            <MapPin size={15} />
                            <span>2. Localização</span>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-12 gap-4">
                            <div className="sm:col-span-4">
                                <label htmlFor="modal-imovel-cidade" className={labelClass}>
                                    Cidade *
                                </label>
                                <input
                                    id="modal-imovel-cidade"
                                    type="text"
                                    value={form.cidade}
                                    onChange={(e) => atualizarCampo('cidade', e.target.value)}
                                    className={inputClass}
                                />
                            </div>

                            <div className="sm:col-span-4">
                                <label htmlFor="modal-imovel-bairro" className={labelClass}>
                                    Bairro *
                                </label>
                                <input
                                    id="modal-imovel-bairro"
                                    type="text"
                                    placeholder="Ex: Colônia do Marçal"
                                    value={form.bairro}
                                    onChange={(e) => atualizarCampo('bairro', e.target.value)}
                                    className={inputClass}
                                />
                            </div>

                            <div className="sm:col-span-4">
                                <label htmlFor="modal-imovel-logradouro" className={labelClass}>
                                    Rua / Logradouro (Opcional)
                                </label>
                                <input
                                    id="modal-imovel-logradouro"
                                    type="text"
                                    placeholder="Ex: Av. Leite de Castro"
                                    value={form.logradouro}
                                    onChange={(e) => atualizarCampo('logradouro', e.target.value)}
                                    className={inputClass}
                                />
                            </div>
                        </div>
                    </div>

                    {/* 3. Cômodos, Áreas e Descrição */}
                    <div className="pt-4 border-t border-gray-100 space-y-4">
                        <div className="grid grid-cols-2 sm:grid-cols-7 gap-3">
                            <div>
                                <label htmlFor="modal-imovel-quartos" className={labelClass}>
                                    Quartos
                                </label>
                                <input
                                    id="modal-imovel-quartos"
                                    type="number"
                                    min="0"
                                    value={form.quartos}
                                    onChange={(e) => atualizarCampo('quartos', e.target.value)}
                                    className={inputClass}
                                />
                            </div>

                            <div>
                                <label htmlFor="modal-imovel-suites" className={labelClass}>
                                    Suítes
                                </label>
                                <input
                                    id="modal-imovel-suites"
                                    type="number"
                                    min="0"
                                    value={form.suites}
                                    onChange={(e) => atualizarCampo('suites', e.target.value)}
                                    className={inputClass}
                                />
                            </div>

                            <div>
                                <label htmlFor="modal-imovel-banheiros" className={labelClass}>
                                    Banheiros
                                </label>
                                <input
                                    id="modal-imovel-banheiros"
                                    type="number"
                                    min="0"
                                    value={form.banheiros}
                                    onChange={(e) => atualizarCampo('banheiros', e.target.value)}
                                    className={inputClass}
                                />
                            </div>

                            <div>
                                <label htmlFor="modal-imovel-vagas" className={labelClass}>
                                    Vagas
                                </label>
                                <input
                                    id="modal-imovel-vagas"
                                    type="number"
                                    min="0"
                                    value={form.vagas}
                                    onChange={(e) => atualizarCampo('vagas', e.target.value)}
                                    className={inputClass}
                                />
                            </div>

                            <div>
                                <label htmlFor="modal-imovel-salas" className={labelClass}>
                                    Salas
                                </label>
                                <input
                                    id="modal-imovel-salas"
                                    type="number"
                                    min="0"
                                    value={form.salas}
                                    onChange={(e) => atualizarCampo('salas', e.target.value)}
                                    className={inputClass}
                                />
                            </div>

                            <div>
                                <label htmlFor="modal-imovel-area-util" className={labelClass}>
                                    Área Útil (m²)
                                </label>
                                <input
                                    id="modal-imovel-area-util"
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    value={form.area_util}
                                    onChange={(e) => atualizarCampo('area_util', e.target.value)}
                                    className={inputClass}
                                />
                            </div>

                            <div>
                                <label htmlFor="modal-imovel-area-total" className={labelClass}>
                                    Área Total (m²)
                                </label>
                                <input
                                    id="modal-imovel-area-total"
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    value={form.area_total}
                                    onChange={(e) => atualizarCampo('area_total', e.target.value)}
                                    className={inputClass}
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="modal-imovel-atributos" className={labelClass}>
                                Diferenciais (separados por vírgula)
                            </label>
                            <input
                                id="modal-imovel-atributos"
                                type="text"
                                placeholder="Ex: Piscina, Churrasqueira, Móveis Planejados, Sol da manhã"
                                value={form.atributos}
                                onChange={(e) => atualizarCampo('atributos', e.target.value)}
                                className={inputClass}
                            />
                        </div>

                        <div>
                            <label htmlFor="modal-imovel-descricao" className={labelClass}>
                                Descrição Detalhada do Imóvel
                            </label>
                            <textarea
                                id="modal-imovel-descricao"
                                rows={3}
                                placeholder="Descreva os detalhes do imóvel, condições de financiamento, proximidade do comércio..."
                                value={form.descricao}
                                onChange={(e) => atualizarCampo('descricao', e.target.value)}
                                className={inputClass}
                            />
                        </div>
                    </div>

                    {/* 4. Galeria de Fotos */}
                    <SecaoGaleriaFotosForm
                        fotos={form.fotos}
                        onAdicionarUrls={handleAdicionarFotos}
                        onRemoverFoto={handleRemoverFoto}
                    />

                    {/* 5. Contato Direto & Redirecionamento */}
                    <div className="pt-4 border-t border-gray-100">
                        <div className="flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-emerald-700 mb-2">
                            <Phone size={15} />
                            <span>5. Contato Direto do Corretor (Para receber os clientes)</span>
                        </div>
                        <p className="text-xs text-gray-500 mb-3">
                            Se você não tiver site próprio, deixe o Link Externo em branco: o botão do imóvel abrirá diretamente uma conversa no seu WhatsApp!
                        </p>

                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            <div>
                                <label htmlFor="modal-imovel-whatsapp" className={labelClass}>
                                    WhatsApp de Atendimento
                                </label>
                                <input
                                    id="modal-imovel-whatsapp"
                                    type="text"
                                    placeholder="(32) 99999-9999"
                                    value={form.whatsapp_contato}
                                    onChange={(e) => atualizarCampo('whatsapp_contato', e.target.value)}
                                    className={inputClass}
                                />
                            </div>

                            <div>
                                <label htmlFor="modal-imovel-telefone" className={labelClass}>
                                    Telefone Secundário
                                </label>
                                <input
                                    id="modal-imovel-telefone"
                                    type="text"
                                    placeholder="(32) 3371-0000"
                                    value={form.telefone_contato}
                                    onChange={(e) => atualizarCampo('telefone_contato', e.target.value)}
                                    className={inputClass}
                                />
                            </div>

                            <div>
                                <label htmlFor="modal-imovel-link" className={labelClass}>
                                    Link Externo (Opcional)
                                </label>
                                <input
                                    id="modal-imovel-link"
                                    type="url"
                                    placeholder="https://seusite.com/imovel..."
                                    value={form.link_externo}
                                    onChange={(e) => atualizarCampo('link_externo', e.target.value)}
                                    className={inputClass}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Rodapé do Modal */}
                    <div className="pt-4 border-t border-gray-100 flex items-center justify-end gap-3">
                        <button
                            type="button"
                            onClick={onFechar}
                            className="px-5 py-2.5 rounded-xl border border-gray-200 text-gray-700 hover:bg-gray-50 text-xs sm:text-sm font-semibold transition-colors"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            disabled={salvando}
                            className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-xs sm:text-sm font-extrabold shadow-sm transition-all"
                        >
                            <Save size={16} />
                            <span>
                                {salvando && 'Salvando...'}
                                {!salvando && (imovelEdicao ? 'Salvar Alterações' : 'Publicar Imóvel')}
                            </span>
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ModalImovelCorretor;
