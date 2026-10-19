const NOME_COOKIE_MATCHES = 'crawty_matches';
const MAX_AGE_SEGUNDOS = 60 * 60 * 24 * 365; // 1 ano
const LIMITE_IDS_COOKIE = 120;
const REGEX_ID_VALIDO = /^[\w-]+$/;

const cacheImoveisMemoria = new Map();

export const validarIdImovel = (id) => {
    if (typeof id !== 'string') return '';
    const limpo = id.trim();
    return REGEX_ID_VALIDO.test(limpo) ? limpo : '';
};

export const lerIdsMatchesCookie = () => {
    if (typeof document === 'undefined' || !document.cookie) {
        return [];
    }

    const partes = document.cookie.split(';');
    for (const parte of partes) {
        const [chaveBruta, ...restoValor] = parte.split('=');
        if (chaveBruta?.trim() === NOME_COOKIE_MATCHES) {
            const valorBruto = restoValor.join('=').trim();
            if (!valorBruto) return [];
            try {
                const decodificado = decodeURIComponent(valorBruto);
                return decodificado
                    .split('|')
                    .map(validarIdImovel)
                    .filter(Boolean);
            } catch {
                return [];
            }
        }
    }
    return [];
};

export const salvarIdsMatchesCookie = (listaIds) => {
    if (typeof document === 'undefined') return [];

    const unicosValidos = [];
    const vistos = new Set();

    for (const item of listaIds) {
        const idValido = validarIdImovel(item);
        if (idValido && !vistos.has(idValido)) {
            vistos.add(idValido);
            unicosValidos.push(idValido);
        }
    }

    const listaFinal = unicosValidos.slice(0, LIMITE_IDS_COOKIE);
    const valorCodificado = encodeURIComponent(listaFinal.join('|'));
    document.cookie = `${NOME_COOKIE_MATCHES}=${valorCodificado}; path=/; max-age=${MAX_AGE_SEGUNDOS}; SameSite=Lax`;

    if (typeof globalThis !== 'undefined' && typeof globalThis.dispatchEvent === 'function') {
        globalThis.dispatchEvent(new CustomEvent('crawty-matches-updated', { detail: listaFinal }));
    }

    return listaFinal;
};

export const adicionarMatchCookie = (imovel) => {
    const idValido = validarIdImovel(imovel?.id_unico);
    if (!idValido) return lerIdsMatchesCookie();

    cacheImoveisMemoria.set(idValido, imovel);
    const atuais = lerIdsMatchesCookie().filter((id) => id !== idValido);
    return salvarIdsMatchesCookie([idValido, ...atuais]);
};

export const removerMatchCookie = (idUnico) => {
    const idValido = validarIdImovel(idUnico);
    const atuais = lerIdsMatchesCookie().filter((id) => id !== idValido);
    return salvarIdsMatchesCookie(atuais);
};

export const limparTodosMatchesCookie = () => {
    return salvarIdsMatchesCookie([]);
};

export const obterImovelCacheMemoria = (idUnico) => {
    return cacheImoveisMemoria.get(idUnico) || null;
};

export const salvarImovelCacheMemoria = (imovel) => {
    const idValido = validarIdImovel(imovel?.id_unico);
    if (idValido) {
        cacheImoveisMemoria.set(idValido, imovel);
    }
};

