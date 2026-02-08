import axios from 'axios';

const API_BASE_URL = '/api/v1';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor - handle errors and token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // Handle 401 - try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                try {
                    const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                        refresh_token: refreshToken,
                    });

                    const { access_token, refresh_token } = response.data;
                    localStorage.setItem('access_token', access_token);
                    localStorage.setItem('refresh_token', refresh_token);

                    originalRequest.headers.Authorization = `Bearer ${access_token}`;
                    return api(originalRequest);
                } catch (refreshError) {
                    // Refresh failed - logout
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('user');
                    window.location.href = '/login';
                }
            }
        }

        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    requestOTP: (mobile) => api.post('/auth/login', { mobile }),
    verifyOTP: (mobile, otp) => api.post('/auth/verify-otp', { mobile, otp }),
    getProfile: () => api.get('/auth/me'),
    logout: () => api.post('/auth/logout'),
};

// Bills API
export const billsAPI = {
    getBills: (params) => api.get('/bills/', { params }),
    getBill: (id) => api.get(`/bills/${id}`),
    payBill: (data) => api.post('/bills/pay', data),
    getPaymentHistory: (params) => api.get('/bills/history/all', { params }),
};

// Grievances API
export const grievancesAPI = {
    create: (data) => api.post('/grievances/', data),
    list: (params) => api.get('/grievances/', { params }),
    get: (id) => api.get(`/grievances/${id}`),
    track: (trackingId) => api.get(`/grievances/track/${trackingId}`),
    submitFeedback: (id, data) => api.post(`/grievances/${id}/feedback`, data),
};

// Connections API
export const connectionsAPI = {
    apply: (data) => api.post('/connections/apply', data),
    list: (params) => api.get('/connections/', { params }),
    get: (id) => api.get(`/connections/${id}`),
    track: (applicationNumber) => api.get(`/connections/track/${applicationNumber}`),
};

// Documents API
export const documentsAPI = {
    upload: (formData) => api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    }),
    list: (params) => api.get('/documents/', { params }),
    get: (id) => api.get(`/documents/${id}`),
    delete: (id) => api.delete(`/documents/${id}`),
};

// Notifications API
export const notificationsAPI = {
    getActive: (params) => api.get('/notifications/', { params }),
    getEmergencies: () => api.get('/notifications/emergencies'),
    getOutages: (params) => api.get('/notifications/outages', { params }),
};

export default api;
