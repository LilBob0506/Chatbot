import axios from "axios";

// const API_BASE = "http://localhost:8000";
const API_BASE = "https://chatbot-9hch.onrender.com"; // your Render URL

export const sendMessage = async (chatId, message) => {
    const token = localStorage.getItem("access_token");
  
    const res = await axios.post(
      `${API_BASE}/send/${chatId}`,
      { message },
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );
  
    return res.data;
  };

export const fetchChats = async () => {
  const token = localStorage.getItem("access_token");
  const res = await fetch("http://localhost:8000/chats", {
      headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) throw new Error("Failed to fetch chats");

  return res.json();
};  

export const fetchChat = async (chatId) => {
    const token = localStorage.getItem("access_token");

    const res = await fetch(`http://localhost:8000/chats/${chatId}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  
    if (!res.ok) throw new Error(`Failed to fetch chat with id ${chatId}`);
  
    return res.json(); // includes messages
  };

export const createChat = async () => {
    const token = localStorage.getItem("access_token");
  
    try {
      const res = await fetch("http://localhost:8000/chats", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`, 
        },
      });
  
      if (!res.ok) {
        throw new Error("Failed to create chat");
      }
  
      const newChat = await res.json();
      return newChat;
    } catch (error) {
      console.error("Error creating chat:", error);
      throw error;
    }
  };

export async function deleteChat(chatId) {
    const token = localStorage.getItem("access_token");
  
    const res = await fetch(`http://127.0.0.1:8000/chats/${chatId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  
    if (!res.ok) {
      throw new Error("Failed to delete chat");
    }
  
    return;
  }  

export const updateChat = async (chatId, newTitle) => {
    const token = localStorage.getItem("access_token");
  
    try {
      const res = await fetch(`http://localhost:8000/chats/${chatId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ title: newTitle }),
      });
  
      if (!res.ok) {
        throw new Error(`Failed to update chat with id ${chatId}`);
      }
  
      return res.json();
    } catch (error) {
      console.error("Error updating chat:", error);
      throw error;
    }
  }

export const fileUpload = async (chatId, file) => {
    const token = localStorage.getItem("access_token");
  
    const formData = new FormData();
    formData.append("file", file);
  
    const res = await axios.post(
      `${API_BASE}/upload/${chatId}`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
          Authorization: `Bearer ${token}`,
        },
      }
    );
  
    return res.data;
  }