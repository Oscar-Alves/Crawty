const CHAVE_TOKEN_CORRETOR = 'crawty_corretor_token';
const REGEX_TOKEN_SEGURO = /^[\w.-]+$/;

let perfilCorretorMemoria = null;

const notificarMudancaAuth = () => {
    if (typeof globalThis !== 'undefined' && typeof globalThis.dispatchEvent === 'function') {
        globalThis.dispatchEvent(new CustomEvent('crawty-auth-updated'));
    }
};

export const validarTokenFormato = (token) => {
    if (typeof token !== 'string') return '';
    const limpo = token.trim();
    return REGEX_TOKEN_SEGURO.test(limpo) ? limpo : '';
};

export const obterTokenCorretor = () => {
    try {
        const salvo = localStorage.getItem(CHAVE_TOKEN_CORRETOR) || '';
        return validarTokenFormato(salvo);
    } catch {
        return '';
    }
};

export const obterPerfilCorretorLocal = () => {
    return perfilCorretorMemoria;
};

export const salvarSessaoCorretor = (token, corretor) => {
    const tokenSeguro = validarTokenFormato(token);
    try {
        if (tokenSeguro) {
            localStorage.setItem(CHAVE_TOKEN_CORRETOR, tokenSeguro);
        }
    } catch {
        // Ignora erro de quota
    }
    if (corretor && typeof corretor === 'object') {
        perfilCorretorMemoria = { ...corretor };
    }
    notificarMudancaAuth();
};

export const atualizarPerfilCorretorLocal = (corretor) => {
    if (corretor && typeof corretor === 'object') {
        perfilCorretorMemoria = { ...corretor };
    }
    notificarMudancaAuth();
};

export const encerrarSessaoCorretor = () => {
    perfilCorretorMemoria = null;
    try {
        localStorage.removeItem(CHAVE_TOKEN_CORRETOR);
    } catch {
        // Ignora erro
    }
    notificarMudancaAuth();
};

export const estaAutenticadoCorretor = () => {
    return Boolean(obterTokenCorretor());
};
