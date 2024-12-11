import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const savePlatformCredentials = async (platform: string, credentials: any) => {
  const response = await axios.post(
    `${API_URL}/credentials/${platform}`,
    credentials
  );
  return response.data;
}; 