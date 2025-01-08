import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

export const blogService = {
  getPopularPosts: async () => {
    try {
      const response = await axios.get(`${API_URL}/blog/posts/popular/`);
      return response.data;
    } catch (error) {
      console.error('Popular posts fetch error:', error);
      throw error;
    }
  }
}; 