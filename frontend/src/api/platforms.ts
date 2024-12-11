import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const getPlatforms = async () => {
  const response = await axios.get(`${API_URL}/platforms`);
  return response.data.platforms;
}; 