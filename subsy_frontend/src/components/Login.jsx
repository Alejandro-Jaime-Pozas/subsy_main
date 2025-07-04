import React, { useState } from "react";

function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);
    try {
      const response = await fetch("/api/users/token/create/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await response.json();
      console.log(data);  // to check response from backend
      if (!response.ok) {
        // Handle Django serializer validation errors
        if (data.non_field_errors && data.non_field_errors.length > 0) {
          throw new Error(data.non_field_errors[0]);
        } else if (data.detail) {
          throw new Error(data.detail);
        } else {
          throw new Error("Login failed");
        }
      }
      localStorage.setItem("authToken", data.token);
      setSuccess(true);
      setForm({ email: "", password: "" });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="email" type="email" placeholder="Email" value={form.email} onChange={handleChange} required />
      <input name="password" type="password" placeholder="Password" value={form.password} onChange={handleChange} required />
      <button type="submit">Login</button>
      {error && <div style={{color: "red"}}>{error}</div>}
      {success && <div style={{color: "green"}}>Login successful!</div>}
    </form>
  );
}

export default Login;
