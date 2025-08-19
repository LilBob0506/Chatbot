import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../api/auth";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await registerUser(email, password); // Call backend
      navigate("/chat"); // Navigate to chat page after registration
    } catch (err) {
      console.error(err);
      alert("Registeration failed");
    }
  };

  return (
    <div className="flex justify-center items-center h-screen w-screen bg-black">
      <form
        onSubmit={handleSubmit}
        className="bg-black p-8 rounded-lg shadow-md w-full max-w-sm"
      >
        <h2 className="text-2xl font-bold text-center mb-6 text-white">
            Register to S-Chatbot
        </h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border border-gray-300 w-full mb-4 p-3 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-xl"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border border-gray-300 w-full mb-6 p-3 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-xl"
          required
        />
        <button
          type="submit"
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold w-full py-3 rounded transition-colors"
        >
          Register
        </button>
        <div className="text-center mt-4 text-white">
          Already have an account?{" "}
          <span
            className="text-blue-500 cursor-pointer hover:underline"
            onClick={() => navigate("/")}
          >
            Sign In
          </span>
        </div>
      </form>
    </div>
  );
}
