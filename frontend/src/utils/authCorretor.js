const CHAVE_TOKEN_CORRETOR = 'crawty_corretor_token';
const CHAVE_PERFIL_CORRETOR = 'crawty_corretor_perfil';

const notificarMudancaAuth = () => {
    if (typeof globalThis !== 'undefined' && typeof globalThis.dispatchEvent === 'function') {
        globalThis.dispatchEvent(new CustomEvent('crawty-auth-updated'));
    }
};

export const obterTokenCorretor = () => {
    try {
        return localStorage.getItem(CHAVE_TOKEN_CORRETOR) || '';
    } catch {
        return '';
    }
};

export const obterPerfilCorretorLocal = () => {
    try {
        const bruto = localStorage.getItem(CHAVE_PERFIL_CORRETOR);
        return bruto ? JSON.parse(bruto) : null;
    } catch {
        return null;
    }
};

export const salvarSessaoCorretor = (token, corretor) => {
    try {
        if (token) {
            localStorage.setItem(CHAVE_TOKEN_CORRETOR, token);
        }
        if (corretor) {
            localStorage.setItem(CHAVE_PERFIL_CORRETOR, JSON.stringify(corretor));
        }
    } catch {
        // Ignora erro de quota
    }
    notificarMudancaAuth();
};

export const atualizarPerfilCorretorLocal = (corretor) => {
    try {
        if (corretor) {
            localStorage.setItem(CHAVE_PERFIL_CORRETOR, JSON.stringify(corretor));
        }
    } catch {
        // Ignora erro de quota
    }
    notificarMudancaAuth();
};

export const encerrarSessaoCorretor = () => {
    try {
        localStorage.removeItem(CHAVE_TOKEN_CORRETOR);
        localStorage.removeItem(CHAVE_PERFIL_CORRETOR);
    } catch {
        // Ignora erro
    }
    notificarMudancaAuth();
};

export const estaAutenticadoCorretor = () => {
    return Boolean(obterTokenCorretor());
};

