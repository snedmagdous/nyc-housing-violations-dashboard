/**
 * API Service Layer
 *
 * This file centralizes all HTTP requests to your FastAPI backend.
 * Benefits:
 * - Single source of truth for API endpoints
 * - Easy to mock for testing
 * - Handles authentication and error handling in one place
 * - Type-safe API calls with TypeScript
 */

import axios, { AxiosError } from 'axios';
import type { AxiosInstance } from 'axios';
import type {
  Violation,
  Building,
  PaginatedResponse,
  ViolationFilters,
  TemporalAggregation,
  ViolationHotspot,
  LandlordRanking,
} from '../types/violation';

/**
 * Base API configuration
 *
 * In development: connects to localhost:8000 (your FastAPI dev server)
 * In production: use environment variable (e.g., VITE_API_URL)
 */
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Create axios instance with default configuration
 * This instance will be used for all API calls
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,  // 10 second timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor - runs before every API call
 * Useful for adding auth tokens, logging, etc.
 */
apiClient.interceptors.request.use(
  (config) => {
    // Log requests in development
    if (import.meta.env.DEV) {
      console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - runs after every API response
 * Handles common error scenarios
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Handle common HTTP errors
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.status, error.response.data);

      switch (error.response.status) {
        case 404:
          console.error('Resource not found');
          break;
        case 500:
          console.error('Server error - check your FastAPI backend logs');
          break;
        case 503:
          console.error('Service unavailable - is your backend running?');
          break;
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('No response from server - is your FastAPI backend running?');
    } else {
      // Something else went wrong
      console.error('Request error:', error.message);
    }

    return Promise.reject(error);
  }
);

/**
 * API Service Object
 * Contains all API endpoint functions organized by domain
 */
export const api = {
  /**
   * VIOLATIONS ENDPOINTS
   */
  violations: {
    /**
     * Get paginated list of violations with optional filters
     *
     * Example usage:
     * const results = await api.violations.getAll({
     *   boro: 'Manhattan',
     *   is_open: true,
     *   page: 1,
     *   per_page: 50
     * });
     */
    getAll: async (filters?: ViolationFilters): Promise<PaginatedResponse<Violation>> => {
      const response = await apiClient.get('/api/violations', { params: filters });
      return response.data;
    },

    /**
     * Get a single violation by ID
     */
    getById: async (id: number): Promise<Violation> => {
      const response = await apiClient.get(`/api/violations/${id}`);
      return response.data;
    },

    /**
     * Get violations for a specific building
     */
    getByBuilding: async (buildingId: number): Promise<Violation[]> => {
      const response = await apiClient.get(`/api/buildings/${buildingId}/violations`);
      return response.data;
    },

    /**
     * Get aggregated violation counts over time
     * Useful for trend charts showing violations by month/year
     */
    getTrends: async (
      groupBy: 'month' | 'quarter' | 'year' = 'month',
      filters?: Omit<ViolationFilters, 'page' | 'per_page'>
    ): Promise<TemporalAggregation[]> => {
      const response = await apiClient.get('/api/violations/trends', {
        params: { group_by: groupBy, ...filters },
      });
      return response.data;
    },
  },

  /**
   * BUILDINGS ENDPOINTS
   */
  buildings: {
    /**
     * Search buildings by address or other criteria
     * Returns aggregated violation statistics for each building
     */
    search: async (query: string): Promise<{ query: string; count: number; buildings: Building[] }> => {
      const response = await apiClient.get('/api/buildings/search', {
        params: { q: query },
      });
      return response.data;
    },

    /**
     * Get detailed information about a specific building
     * Includes all aggregated violation statistics
     */
    getById: async (buildingId: number): Promise<Building> => {
      const response = await apiClient.get(`/api/buildings/${buildingId}`);
      return response.data;
    },

    /**
     * Get buildings within a geographic bounding box
     * Used for map view to show only buildings in the visible area
     *
     * @param bounds - Geographic bounding box [minLat, minLng, maxLat, maxLng]
     */
    getInBounds: async (bounds: [number, number, number, number]): Promise<Building[]> => {
      const [minLat, minLng, maxLat, maxLng] = bounds;
      const response = await apiClient.get('/api/buildings/in-bounds', {
        params: { min_lat: minLat, min_lng: minLng, max_lat: maxLat, max_lng: maxLng },
      });
      return response.data;
    },
  },

  /**
   * ANALYSIS ENDPOINTS
   */
  analysis: {
    /**
     * Get violation hotspots (geographic clusters)
     * Returns high-concentration areas for map visualization
     */
    getHotspots: async (boro?: string): Promise<ViolationHotspot[]> => {
      const response = await apiClient.get('/api/analysis/hotspots', {
        params: { boro },
      });
      return response.data;
    },

    /**
     * Get landlord rankings (worst offenders)
     * Sorted by total violations, severity, or risk score
     */
    getLandlordRankings: async (
      sortBy: 'total_violations' | 'severe_violations' | 'risk_score' = 'total_violations',
      limit: number = 50
    ): Promise<LandlordRanking[]> => {
      const response = await apiClient.get('/api/analysis/landlord-rankings', {
        params: { sort_by: sortBy, limit },
      });
      return response.data;
    },

    /**
     * Get statistics summary
     * Overall dashboard metrics: total violations, open violations, etc.
     */
    getStats: async () => {
      const response = await apiClient.get('/api/analysis/stats');
      return response.data;
    },
  },
};

/**
 * Export the axios instance for advanced use cases
 * Most components should use the 'api' object above instead
 */
export default apiClient;
