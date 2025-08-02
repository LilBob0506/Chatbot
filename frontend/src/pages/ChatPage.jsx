import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { sendMessage, createChat, fetchChats, fetchChat, deleteChat, updateChat, fileUpload } from '../api/chat';

export default function OpenWebUIClone() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const [isLoading, setIsLoading] = useState(false);

  const [currentChatId, setCurrentChatId] = useState(null);
  const chatIdRef = useRef(null);

  const [chatHistory, setChatHistory] = useState([]);
  const navigate = useNavigate();

  const [editingChatId, setEditingChatId] = useState(null);
  const [editingTitle, setEditingTitle] = useState("");


  // Load chat history on component mount
  useEffect(() => {
    const token = localStorage.getItem("access_token");

    if (!token) {
      navigate("/"); // Kick user back to login
      return;
    }
    const loadChats = async () => {
      const token = localStorage.getItem("access_token");

      if (!token) {
        console.warn("No token found, redirecting to login.");
        navigate("/");
        return;
      }

      try {
        const chats = await fetchChats(); // fetchChats must send the token
        setChatHistory(chats);
      } catch (err) {
        console.error("Failed to load chats", err);
        if (err.message.includes("Unauthorized")) {
          localStorage.removeItem("access_token");
          navigate("/");
        }
      }
    };

    loadChats();
  }, [navigate]);

  const handleSend = async () => {
    if (!input.trim()) return;
  
    setMessages((prev) => [...prev, { from: "user", text: input }]);
    setInput('');
    setIsLoading(true);
    console.log("Sending message:", input);
  
    try {
      let chatId = chatIdRef.current;
      console.log("Current chatIdRef:", chatIdRef.current);

      // If chat doesn't exist, create one
      if (!chatId) {
        console.log("Creating new chat...");
        const newChat = await createChat();
        console.log("New chat:", newChat);
        chatId = newChat.id;
        setCurrentChatId(chatId);
        chatIdRef.current = chatId;

        // Re-fetch all chats to show the new one in the sidebar
        const updatedChats = await fetchChats();
        setChatHistory(updatedChats);
      }
  
      const reply = await sendMessage(chatId, input);
      console.log("Received reply:", reply);
      setMessages((prev) => [...prev, { from: "assistant", text: reply.reply }]);
    } catch (err) {
      console.error("Failed to send message:", err);
      handleLogout(); // Logout if there's an error
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = async () => {
    setMessages([]);           
    setCurrentChatId(null);
    chatIdRef.current = null;

    try {
      const newChat = await createChat();
      console.log("Created new chat:", newChat);
      setCurrentChatId(newChat.id);
      chatIdRef.current = newChat.id;

      // Re-fetch all chats to show the new one in the sidebar
    const updatedChats = await fetchChats();
    setChatHistory(updatedChats);
  
    } catch (err) {
      console.error("Failed to create new chat:", err);
      handleLogout(); // Logout if there's an error
    }
  };

  const handleSelectChat = async (chatId) => {
    try {
      const chat = await fetchChat(chatId);
  
      const formattedMessages = chat.messages.map((msg) => ({
        from: msg.sender === "user" ? "user" : "assistant",
        text: msg.content,
      }));
  
      setMessages(formattedMessages);
      setCurrentChatId(chat.id);
      chatIdRef.current = chat.id;
    } catch (err) {
      console.error("Failed to load chat messages:", err);
      handleLogout(); // Logout if there's an error
    }
  };

  const handleDeleteChat = async (chatId) => {
    try {
      await deleteChat(chatId);

       // Re-fetch all chats to show the new one in the sidebar
      const updatedChats = await fetchChats();
      setChatHistory(updatedChats);
      
      // If deleting current chat, clear it
      if (currentChatId === chatId) {
        chatIdRef.current = null;
        setCurrentChatId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error("Failed to delete chat", err);
    }
  };

  const startEditing = (id, currentTitle) => {
    setEditingChatId(id);
    setEditingTitle(currentTitle || "");
  };
  
  const handleUpdateTitle = async (id) => {
    try {
      await updateChat(id, editingTitle); // Your backend call
      const updatedChats = await fetchChats(); // Refresh local state
      setChatHistory(updatedChats);
    } catch (err) {
      console.error("Failed to update chat title", err);
    } finally {
      setEditingChatId(null);
      setEditingTitle("");
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !currentChatId) return;
  
    try {
      const reply = await fileUpload(currentChatId, file);
      setMessages((prev) => [
        ...prev,
        { from: "user", text: `${file.name}]` }
      ]);
      console.log("Upload success:", reply);
      setMessages((prev) => [...prev, { from: "assistant", text: reply.reply }
      ]);
    } catch (err) {
      console.error("Upload failed:", err);
    }
  };
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");   
    navigate("/");                             
  };

  return (
    <div className="flex h-screen w-screen bg-gray-900">

      {/* Sidebar */}
      <aside className="w-64 bg-black border-r border-gray-700 flex flex-col">
        {/* New Chat Button */}
        <div className="p-4">
          <button 
          onClick={handleNewChat}
          className="w-full bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded-lg border border-gray-600 transition-colors">
            + New Chat
          </button>
        </div>

        {/* Chat History */}
        <aside className="w-64 bg-black p-4 overflow-y-auto">
          <h2 className="font-bold mb-4 text-white">Chat History</h2>
          {chatHistory.map((chat) => (
            <div
            key={chat.id}
              className={`relative group flex items-center justify-between p-2 mb-2 rounded text-white 
              ${chat.id === currentChatId ? 'bg-gray-700 border-l-4 border-blue-500' : 'bg-gray-800 hover:bg-gray-700'}`}
            >
              {/* Chat title or edit input */}
              <div
                onClick={() => handleSelectChat(chat.id)}
                className="flex-1 truncate pr-22"
              >
                {editingChatId === chat.id ? (
                  <input
                    value={editingTitle}
                    onChange={(e) => setEditingTitle(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") handleUpdateTitle(chat.id);
                    }}
                    className="bg-gray-700 text-white p-1 rounded w-full"
                    autoFocus
                  />
                ) : (
                  <span>{chat.title || `Chat ${chat.id}`}</span>
                )}
              </div>

              {/* Edit / Save Icon */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  if (editingChatId === chat.id) {
                    handleUpdateTitle(chat.id);
                  } else {
                    startEditing(chat.id, chat.title);
                  }
                }}
                className="absolute right-13 top-1/2 transform -translate-y-1/2 text-blue-400 hover:text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity duration-200 w-5 h-5 text-xs flex items-center justify-center"
                title={editingChatId === chat.id ? "Save" : "Edit"}
              >
                {editingChatId === chat.id ? "✅" : "✏️"}
              </button>

             {/* Cancel or Delete Button */}
              {editingChatId === chat.id ? (
                // Cancel button in place of Delete
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setEditingChatId(null);
                    setEditingTitle("");
                  }}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-200 transition-opacity duration-200 w-5 h-5 text-xs flex items-center justify-center"
                  title="Cancel"
                >
                  ❌
                </button>
              ) : (
                // Delete button (normal mode)
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteChat(chat.id);
                  }}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-red-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity duration-200 w-5 h-5 text-xs flex items-center justify-center"
                  title="Delete chat"
                >
                  &times;
                </button>
              )}
            </div>
          ))}
        </aside>

        {/* Settings/Profile */}
        <div className="p-4 border-t border--700 mt-auto">
          <div className="flex items-center space-x-2 text-gray-300 cursor-pointer hover:text-white">
            <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center text-sm">
              U
            </div>
            <span className="text-sm">User</span>   
          </div>
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col">
        {/* Header */}
        <header className="flex bg-black border-b border-gray-700 p-4">
          <h2 className="text-white text-lg font-medium">S-Chatbot</h2>
          <button
            onClick={handleLogout}
            className="flex ml-auto text-xs bg-red-500 text-white p-1 rounded hover:bg-red-600"
          >
            Logout
          </button>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.from === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-3xl ${
                msg.from === 'user' 
                  ? 'ml-auto' 
                  : 'mr-auto'
              }`}>
                {msg.from === 'assistant' && (
                  <div className="flex items-start space-x-3 mb-2">
                    <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-medium">
                      AI
                    </div>
                    <div className="text-gray-300 text-sm font-medium">Assistant</div>
                  </div>
                )}
                <div className={`p-4 rounded-lg break-words whitespace-pre-wrap max-w-full ${
                  msg.from === 'user'
                    ? 'bg-blue-600 text-white ml-12'
                    : 'bg-gray-800 text-gray-100 border border-gray-700'
                }`}>
                  {msg.text}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Input Area */}
<div className="p-4 bg-gray-800 border-t border-gray-700">
  <div className="max-w-4xl mx-auto">
    <div className="flex items-center space-x-2">

      {/* Upload Button */}
      <label className="relative cursor-pointer bg-gray-700 hover:bg-gray-600 text-white p-3 rounded-md text-sm flex items-center justify-center h-10">
        📁
        <input
          type="file"
          onChange={handleFileUpload}
          className="absolute inset-0 opacity-0 cursor-pointer"
        />
      </label>
      
      {/* Text Input Area */}
      <div className="flex-1 relative">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="w-full bg-gray-700 text-white border border-gray-600 rounded-lg p-3 pr-12 resize-none focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          placeholder="Send a message..."
          rows="1"
          onKeyDown={handleKeyDown}
        />

        {/* Send Button */}
        <button
          onClick={handleSend}
          disabled={!input.trim()}
          className="absolute right-2 bottom-2 w-8 h-10 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-md flex items-center justify-center transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>

    </div>
  </div>
</div>

      </main>
    </div>
  );
}