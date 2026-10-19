import { obterTokenCorretor, encerrarSessaoCorretor } from "../utils/authCorretor";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const STATUS_PERMITIDOS = new Set(["ativos", "descontinuados", "todos"]);

const montarHeadersAutenticados = (incluirJson = false) => {
    const token = obterTokenCorretor();
    const headers = {};
    if (incluirJson) {
        headers["Content-Type"] = "application/json";
    }
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }
    return headers;
};

export const getFiltros = async (status = "ativos") => {
    try {
        const statusSeguro = STATUS_PERMITIDOS.has(status) ? status : "ativos";
        const query = new URLSearchParams({ status: statusSeguro });
        const response = await fetch(`${API_URL}/filtros?${query.toString()}`);
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
    const idTexto = String(id || "").trim();
    if (!/^[\w-]+$/.test(idTexto)) {
        throw new Error("Identificador de imóvel inválido");
    }
    const response = await fetch(`${API_URL}/imoveis/${encodeURIComponent(idTexto)}`);
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
    const response = await fetch(`${API_URL}/estatisticas${query}`, {
        headers: montarHeadersAutenticados(false),
    });
    if (response.status === 401) {
        encerrarSessaoCorretor();
        const erroAuth = new Error("Acesso restrito a corretores autenticados.");
        erroAuth.status = 401;
        throw erroAuth;
    }
    if (!response.ok) throw new Error("Erro ao carregar estatísticas de mercado");
    return await response.json();
};

export const loginCorretorApi = async (usuario, senha) => {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario, senha }),
    });
    const dados = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(dados.detail || "Não foi possível realizar o login.");
    }
    return dados;
};

export const obterMeuPerfilCorretorApi = async () => {
    const response = await fetch(`${API_URL}/auth/me`, {
        headers: montarHeadersAutenticados(false),
    });
    if (response.status === 401) {
        encerrarSessaoCorretor();
        const erroAuth = new Error("Sessão expirada.");
        erroAuth.status = 401;
        throw erroAuth;
    }
    if (!response.ok) throw new Error("Erro ao carregar dados do corretor.");
    return await response.json();
};

export const atualizarPerfilCorretorApi = async (payload) => {
    const response = await fetch(`${API_URL}/auth/perfil`, {
        method: "PUT",
        headers: montarHeadersAutenticados(true),
        body: JSON.stringify(payload),
    });
    const dados = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(dados.detail || "Não foi possível atualizar o perfil.");
    }
    return dados;
};

const validarIdUnicoUrl = (idUnico) => {
    const limpo = String(idUnico || "").trim();
    if (!/^[\w-]+$/.test(limpo)) {
        throw new Error("Identificador de imóvel inválido.");
    }
    return encodeURIComponent(limpo);
};

export const listarMeusImoveisCorretorApi = async () => {
    const response = await fetch(`${API_URL}/corretor/imoveis`, {
        headers: montarHeadersAutenticados(false),
    });
    if (response.status === 401) {
        encerrarSessaoCorretor();
        const erroAuth = new Error("Sessão expirada.");
        erroAuth.status = 401;
        throw erroAuth;
    }
    if (!response.ok) throw new Error("Erro ao carregar sua carteira de imóveis.");
    return await response.json();
};

export const cadastrarImovelCorretorApi = async (payload) => {
    const response = await fetch(`${API_URL}/corretor/imoveis`, {
        method: "POST",
        headers: montarHeadersAutenticados(true),
        body: JSON.stringify(payload),
    });
    const dados = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(dados.detail || "Não foi possível cadastrar o imóvel.");
    }
    return dados;
};

export const editarImovelCorretorApi = async (idUnico, payload) => {
    const idSeguro = validarIdUnicoUrl(idUnico);
    const response = await fetch(`${API_URL}/corretor/imoveis/${idSeguro}`, {
        method: "PUT",
        headers: montarHeadersAutenticados(true),
        body: JSON.stringify(payload),
    });
    const dados = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(dados.detail || "Não foi possível atualizar o imóvel.");
    }
    return dados;
};

export const alterarStatusImovelCorretorApi = async (idUnico, ativo) => {
    const idSeguro = validarIdUnicoUrl(idUnico);
    const response = await fetch(`${API_URL}/corretor/imoveis/${idSeguro}/status`, {
        method: "PATCH",
        headers: montarHeadersAutenticados(true),
        body: JSON.stringify({ ativo: Boolean(ativo) }),
    });
    const dados = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(dados.detail || "Não foi possível alterar o status do imóvel.");
    }
    return dados;
};

export const excluirImovelCorretorApi = async (idUnico) => {
    const idSeguro = validarIdUnicoUrl(idUnico);
    const response = await fetch(`${API_URL}/corretor/imoveis/${idSeguro}`, {
        method: "DELETE",
        headers: montarHeadersAutenticados(false),
    });
    const dados = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(dados.detail || "Não foi possível excluir o imóvel.");
    }
    return dados;
};

export const obterMetricasCorretorApi = async () => {
    const response = await fetch(`${API_URL}/corretor/metricas`, {
        method: "GET",
        headers: montarHeadersAutenticados(false),
    });
    const dados = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(dados.detail || "Não foi possível carregar as métricas.");
    }
    return dados;
};

export const impulsionarImovelCorretorApi = async (idUnico, { dias = 15, plano = "15dias" } = {}) => {
    const idSeguro = validarIdUnicoUrl(idUnico);
    const response = await fetch(`${API_URL}/corretor/imoveis/${idSeguro}/impulsionar`, {
        method: "POST",
        headers: montarHeadersAutenticados(true),
        body: JSON.stringify({ dias, plano }),
    });
    const dados = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(dados.detail || "Não foi possível impulsionar o imóvel.");
    }
    return dados;
};

export const cancelarImpulsionamentoCorretorApi = async (idUnico) => {
    const idSeguro = validarIdUnicoUrl(idUnico);
    const response = await fetch(`${API_URL}/corretor/imoveis/${idSeguro}/impulsionar`, {
        method: "DELETE",
        headers: montarHeadersAutenticados(false),
    });
    const dados = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(dados.detail || "Não foi possível cancelar o impulsionamento.");
    }
    return dados;
};