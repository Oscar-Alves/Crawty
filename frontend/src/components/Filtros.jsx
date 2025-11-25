import { Filter } from 'lucide-react';

const Filtros = ({ opcoes, filtros, setFiltros }) => {
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFiltros(prev => ({ ...prev, [name]: value }));
    };

    const selectClass = "w-full p-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all hover:bg-white";
    const labelClass = "block text-xs font-bold text-gray-600 uppercase tracking-wider mb-1.5 ml-1";

    return (
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-8">
            <div className="flex items-center gap-2 mb-4 text-gray-800">
                <Filter size={20} className="text-blue-600"/>
                <h2 className="font-bold text-lg">Filtrar Imóveis</h2>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                <div>
                    <label className={labelClass}>Cidade</label>
                    <select name="cidade" value={filtros.cidade} onChange={handleChange} className={selectClass}>
                        <option value="">Todas as Cidades</option>
                        {opcoes.cidades.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                </div>

                <div>
                    <label className={labelClass}>Bairro</label>
                    <select name="bairro" value={filtros.bairro} onChange={handleChange} className={selectClass} disabled={!filtros.cidade}>
                        <option value="">Todos os Bairros</option>
                        {opcoes.bairros.map(b => <option key={b} value={b}>{b}</option>)}
                    </select>
                </div>

                 <div>
                    <label className={labelClass}>Tipo</label>
                    <select name="tipo" value={filtros.tipo} onChange={handleChange} className={selectClass}>
                        <option value="">Todos os Tipos</option>
                        {opcoes.tipos.map(t => <option key={t} value={t}>{t}</option>)}
                    </select>
                </div>

                <div>
                    <label className={labelClass}>Finalidade</label>
                    <select name="modalidade" value={filtros.modalidade} onChange={handleChange} className={selectClass}>
                        <option value="">Todas</option>
                        <option value="VENDA">Comprar</option>
                        <option value="ALUGUEL">Alugar</option>
                    </select>
                </div>

                <div>
                    <label className={labelClass}>Ordenar</label>
                    <select name="ordenar_por" value={filtros.ordenar_por} onChange={handleChange} className={selectClass}>
                        <option value="">Padrão</option>
                        <option value="menor_preco">Menor Preço</option>
                        <option value="maior_preco">Maior Preço</option>
                        <option value="recente">Mais Recentes</option>
                    </select>
                </div>
            </div>
        </div>
    );
};

export default Filtros;