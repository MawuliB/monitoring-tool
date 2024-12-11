import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const fetchLogs = async (filters: any) => {
  try {
    const response = await axios.get(`${API_URL}/logs`, { 
      params: filters,
      validateStatus: (status) => status < 500 // Don't throw on 401
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching logs:', error);
    return [];
  }
}; 