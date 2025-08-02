import axios from "axios";

const API_URL = "http://localhost:8000"; // Add backend proxy/CORS later

// export const loginUser = (email, password) =>
//   axios.post(`${API_URL}/login`, { email, password });

// export const sendMessage = (message, token) =>
//   axios.post(
//     `${API_URL}/send`,
//     { message },
//     { headers: { Authorization: `Bearer ${token}` } }
//   );

// Add Authorization header if token exists
API.interceptors.request.use((req) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    req.headers.Authorization = `Bearer ${token}`;
  }
  return req;
});

// Auth APIs
export const loginUser = (credentials) => API.post("/login", credentials);
export const registerUser = (credentials) => API.post("/register", credentials);
export const refreshToken = (token) => API.post("/refresh", { refresh_token: token });

// Chat APIs
export const createChat = () => API.post("/chats");
export async function fetchChats(token) {
  const response = await axios.get('/chats', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}
export const getChat = (chatId) => API.get(`/chats/${chatId}`);
export const sendMessage = (chatId, message) =>
  API.post(`/send/${chatId}`, { message });
export const deleteChat = (chatId) => API.delete(`/chats/${chatId}`);
export const updateChatTitle = (chatId, title) =>
  API.patch(`/chats/${chatId}`, { title });

// Messages APIs
export const deleteMessage = (messageId) => API.delete(`/messages/${messageId}`);
export const updateMessage = (messageId, content) =>
  API.patch(`/messages/${messageId}`, { content });

// File upload
export const uploadFile = (chatId, file) => {
  const formData = new FormData();
  formData.append("file", file);
  return API.post(`/upload/${chatId}`, formData);
};

// Stats
export const getUserStats = () => API.get("/stats");