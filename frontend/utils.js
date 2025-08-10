import { API_BASE_URL } from './constants';

/**
 * 画像のURLを正規化します。
 * - URLがnullまたは未定義の場合はそのまま返します。
 * - URLが'http'で始まる場合は、すでに完全なURLとみなし、そのまま返します。
 * - 上記以外の場合は、API_BASE_URLを先頭に付与して返します。
 * @param {string | null | undefined} url - 正規化する画像のURL
 * @returns {string | null | undefined} 正規化されたURL
 */
export const normalizeImageUrl = (url) => {
  if (!url) {
    return url;
  }
  if (url.startsWith('http')) {
    return url;
  }
  return `${API_BASE_URL}${url}`;
};