import axios from "axios";
import { useState, useEffect } from "react";

const API_BASE_URL = "http://127.0.0.1:8000"; // FastAPI backend

export async function loginUser(email, password) {

  const response = await axios.post(`${API_BASE_URL}/login`, {
    email,
    password,
  });

  // Store token in localStorage
  localStorage.setItem("access_token", response.data.access_token);
  return response.data;
}

export async function registerUser(email, password) {

  const response = await axios.post(`${API_BASE_URL}/users`, {
    email,
    password,
  });

  // Store token in localStorage
  localStorage.setItem("access_token", response.data.access_token);
  return response.data;
}

export function getAccessToken() {
  return localStorage.getItem("access_token");
}
