import { createContext, useState, useEffect } from "react";
import { refreshToken } from "../api";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  const login = (accessToken, refreshTokenValue) => {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshTokenValue);
    setUser({ accessToken });
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
  };

  useEffect(() => {
    const token = localStorage.getItem("refresh_token");
    if (token) {
      refreshToken(token)
        .then((res) => {
          login(res.data.access_token, token);
        })
        .catch(() => logout());
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
