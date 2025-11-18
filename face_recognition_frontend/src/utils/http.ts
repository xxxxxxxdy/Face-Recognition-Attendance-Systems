import axios from 'axios';

const request = axios.create({
    baseURL: import.meta.env.VITE_APP_BASE_API,
    timeout: 5000,
});

const excludeAuthPaths = ['/login'];

function shouldExcludeAuth(url: string | undefined): boolean {
    if (!url) return false;
    return excludeAuthPaths.some(path => url.startsWith(path));
}

request.interceptors.request.use(
    (config) => {
        if (config.url && shouldExcludeAuth(config.url)) {
            return config;
        }

        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        if (config.method === 'post' && !(config.data instanceof FormData) && !config.headers['Content-Type']) {
            config.headers['Content-Type'] = 'application/json';
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export default request;