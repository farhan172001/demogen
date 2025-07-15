import React, { useState } from "react";
import axios from "axios";

export default function SignUpPage() {
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    phone: '',
    company: '',
    jobRole: '',
    email: '',
    username: '',
    password: ''
  });

  const [message, setMessage] = useState('');

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/signup', form);
      setMessage('Account created. Please log in.');
      setTimeout(() => {
        window.location.href = '/login'; // ✅ Redirect after success
      }, 1500);
    } catch (err) {
      setMessage('Signup failed. User may already exist.');
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-gray-100">
      <form onSubmit={handleSignup} className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-4">Sign Up</h2>

        {message && <p className="text-sm mb-2 text-center text-red-600">{message}</p>}

        <input name="firstName" placeholder="First Name" value={form.firstName} onChange={handleChange} required className="w-full p-2 mb-3 border rounded" />
        <input name="lastName" placeholder="Last Name" value={form.lastName} onChange={handleChange} required className="w-full p-2 mb-3 border rounded" />
        <input name="phone" placeholder="Phone Number" value={form.phone} onChange={handleChange} required className="w-full p-2 mb-3 border rounded" />
        <input name="company" placeholder="Company Name" value={form.company} onChange={handleChange} required className="w-full p-2 mb-3 border rounded" />
        <input name="jobRole" placeholder="Job Role" value={form.jobRole} onChange={handleChange} required className="w-full p-2 mb-3 border rounded" />
        <input type="email" name="email" placeholder="Email" value={form.email} onChange={handleChange} required className="w-full p-2 mb-3 border rounded" />
        <input name="username" placeholder="Username" value={form.username} onChange={handleChange} required className="w-full p-2 mb-3 border rounded" />
        <input type="password" name="password" placeholder="Password" value={form.password} onChange={handleChange} required className="w-full p-2 mb-4 border rounded" />

        <button type="submit" className="w-full bg-green-500 text-white py-2 rounded hover:bg-green-600">
          Sign Up
        </button>
      </form>
    </div>
  );
}
