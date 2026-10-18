const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export const getFiltros = async (status = "ativos") => {
    try {
        const response = await fetch(`${API_URL}/filtros?status=${encodeURIComponent(status)}`);
        if (!response.ok) throw new Error("Erro ao buscar opções de filtro");
        return await response.json();
    } catch (error) {
        console.error("Erro ao buscar filtros", error);
        return {
            cidades: [],
            bairros: [],
            bairros_por_cidade: {},
            tipos: [],
            subtipos: [],
            subtipos_por_tipo: {},
            imobiliarias: [],
            modalidades: ["VENDA", "ALUGUEL"],
        };
    }
};

export const getImoveis = async (params) => {
    const query = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== "" && value !== false) {
            query.append(key, value);
        }
    });

    const response = await fetch(`${API_URL}/imoveis?${query.toString()}`);

    if (!response.ok) throw new Error("Erro ao buscar imóveis do servidor");

    return await response.json();
};

export const getImovelDetalhes = async (id) => {
    const response = await fetch(`${API_URL}/imoveis/${id}`);
    if (!response.ok) throw new Error("Imóvel não encontrado");
    return await response.json();
};

export const registrarCliqueLead = (idUnico, origem = "detalhes") => {
    try {
        fetch(`${API_URL}/leads/clique`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id_unico: idUnico, origem }),
            keepalive: true,
        }).catch(() => {});
    } catch {
        // Silencioso para nunca bloquear o redirecionamento do usuário
    }
};

export const getEstatisticas = async (cidade = "") => {
    const query = cidade ? `?cidade=${encodeURIComponent(cidade)}` : "";
    const response = await fetch(`${API_URL}/estatisticas${query}`);
    if (!response.ok) throw new Error("Erro ao carregar estatísticas de mercado");
    return await response.json();
};