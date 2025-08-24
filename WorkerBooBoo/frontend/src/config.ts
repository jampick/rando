// API Configuration
export const API_CONFIG = {
  // Automatically detect the correct API base URL
  getBaseUrl: (): string => {
    // If we're running on localhost, use localhost:8000
    if (window.location.hostname === 'localhost') {
      return 'http://localhost:8000';
    }
    
    // If we're running on a local network IP, use the same IP with port 8000
    if (window.location.hostname.match(/^192\.168\.|^10\.|^172\./)) {
      return `http://${window.location.hostname}:8000`;
    }
    
    // Default fallback
    return 'http://localhost:8000';
  },
  
  // Get the full API URL for a specific endpoint
  getApiUrl: (endpoint: string): string => {
    return `${API_CONFIG.getBaseUrl()}${endpoint}`;
  }
};
