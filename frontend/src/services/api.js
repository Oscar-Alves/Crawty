const API_URL = "http://127.0.0.1:8000";

export const getFiltros = async () => {
    try {
        const response = await fetch(`${API_URL}/filtros`);
        return await response.json();
    } catch (error) {
        console.error("Erro ao buscar filtros", error);
        return { cidades: [], bairros: [], tipos: [] };
    }
};

export const getImoveis = async (params) => {
    const query = new URLSearchParams();
    // Limpa parâmetros vazios antes de enviar
    Object.entries(params).forEach(([key, value]) => {
        if (value) query.append(key, value);
    });

    const response = await fetch(`${API_URL}/imoveis?${query.toString()}`);
    return await response.json();
};

export const getImovelDetalhes = async (id) => {
    const response = await fetch(`${API_URL}/imoveis/${id}`);
    if (!response.ok) throw new Error('Imóvel não encontrado');
    return await response.json();
};