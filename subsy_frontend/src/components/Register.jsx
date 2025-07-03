import React, { useState } from "react";

function Register() {
  const [form, setForm] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
  });
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
      const response = await fetch("/api/users/create/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Registration failed");
      }
      setSuccess(true);
      setForm({ email: "", password: "", first_name: "", last_name: "" });
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="email" type="email" placeholder="Email" value={form.email} onChange={handleChange} required />
      <input name="password" type="password" placeholder="Password" value={form.password} onChange={handleChange} required minLength={8} />
      <input name="first_name" type="text" placeholder="First Name" value={form.first_name} onChange={handleChange} />
      <input name="last_name" type="text" placeholder="Last Name" value={form.last_name} onChange={handleChange} />
      <button type="submit">Register</button>
      {error && <div style={{color: "red"}}>{error}</div>}
      {success && <div style={{color: "green"}}>Registration successful!</div>}
    </form>
  );
}

export default Register;
