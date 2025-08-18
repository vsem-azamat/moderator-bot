import axios from 'axios';
import type { Chat, ChatStats, ChatUpdateData } from '../types/chat';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatAPI = {
  // Get all chats
  getChats: async (): Promise<Chat[]> => {
    const response = await api.get('/chats');
    return response.data;
  },

  // Get specific chat
  getChat: async (chatId: number): Promise<Chat> => {
    const response = await api.get(`/chats/${chatId}`);
    return response.data;
  },

  // Update chat configuration
  updateChat: async (chatId: number, updateData: ChatUpdateData): Promise<Chat> => {
    const response = await api.put(`/chats/${chatId}`, updateData);
    return response.data;
  },

  // Get chat statistics
  getChatStats: async (chatId: number): Promise<ChatStats> => {
    const response = await api.get(`/chats/${chatId}/stats`);
    return response.data;
  },

  // Bulk update chats
  bulkUpdateChats: async (chatIds: number[], updateData: ChatUpdateData): Promise<Chat[]> => {
    const response = await api.post('/chats/bulk-update', {
      chat_ids: chatIds,
      update_data: updateData,
    });
    return response.data;
  },
};

export default api;
