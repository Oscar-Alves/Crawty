export const FOTO_FALLBACK = 'https://placehold.co/600x400.png?text=Sem+Foto';

const BUNNY_CDN_BASE = 'https://homeclix.b-cdn.net';

/**
 * Converte URLs do S3 (Homeclix / DataClix) para o endpoint oficial de CDN (BunnyCDN),
 * evitando erros 403 Forbidden causados por buckets privados da AWS.
 *
 * Ex: https://homeclix.s3.amazonaws.com/homeclix/3/... -> https://homeclix.b-cdn.net/3/...
 */
export const normalizarUrlFoto = (url) => {
    if (!url || typeof url !== 'string') return FOTO_FALLBACK;
    const limpa = url.trim();
    if (!limpa) return FOTO_FALLBACK;

    // Padrão que captura variantes s3.amazonaws.com do Homeclix / crmdataclix
    const regexS3 = /^https?:\/\/(?:(?:homeclix|crmdataclix)\.s3(?:\.[a-z0-9-]+)?\.amazonaws\.com\/homeclix\/|s3(?:\.[a-z0-9-]+)?\.amazonaws\.com\/(?:homeclix|crmdataclix)\/homeclix\/)/i;
    if (regexS3.test(limpa)) {
        return limpa.replace(regexS3, `${BUNNY_CDN_BASE}/`);
    }

    return limpa;
};

