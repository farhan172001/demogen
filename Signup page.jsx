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




return (
  <div className="flex items-center justify-center min-h-screen bg-gray-100 px-4">
    <form onSubmit={handleSignup} className="bg-white p-8 rounded shadow-md w-full max-w-lg">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Sign Up</h2>

      {message && (
        <p className="text-sm mb-4 text-center text-red-600">{message}</p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <input
          name="firstName"
          placeholder="First Name"
          value={form.firstName}
          onChange={handleChange}
          required
          className="p-2 border rounded w-full"
        />
        <input
          name="lastName"
          placeholder="Last Name"
          value={form.lastName}
          onChange={handleChange}
          required
          className="p-2 border rounded w-full"
        />
        <input
          name="phone"
          placeholder="Phone Number"
          value={form.phone}
          onChange={handleChange}
          required
          className="p-2 border rounded w-full"
        />
        <input
          name="company"
          placeholder="Company Name"
          value={form.company}
          onChange={handleChange}
          required
          className="p-2 border rounded w-full"
        />
        <input
          name="jobRole"
          placeholder="Job Role"
          value={form.jobRole}
          onChange={handleChange}
          required
          className="p-2 border rounded w-full"
        />
        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
          className="p-2 border rounded w-full"
        />
        <input
          name="username"
          placeholder="Username"
          value={form.username}
          onChange={handleChange}
          required
          className="p-2 border rounded w-full"
        />
        <input
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          required
          className="p-2 border rounded w-full"
        />
      </div>

      <button
        type="submit"
        className="w-full mt-6 bg-green-600 text-white py-2 rounded hover:bg-green-700 transition"
      >
        Sign Up
      </button>
    </form>
  </div>
);


// new
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
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await axios.post('/api/signup', form);
      setMessage('Account created successfully! Redirecting to login...');
      setTimeout(() => {
        window.location.href = '/login';
      }, 1500);
    } catch (err) {
      setMessage('Signup failed. User may already exist.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Account</h1>
            <p className="text-gray-600">Join us today and get started</p>
          </div>

          {/* Message */}
          {message && (
            <div className={`mb-6 p-4 rounded-lg text-center ${
              message.includes('successfully') 
                ? 'bg-green-50 text-green-700 border border-green-200' 
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {message}
            </div>
          )}

          <form onSubmit={handleSignup} className="space-y-6">
            {/* Personal Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    First Name
                  </label>
                  <input 
                    name="firstName" 
                    placeholder="Enter your first name" 
                    value={form.firstName} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 placeholder-gray-400"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Last Name
                  </label>
                  <input 
                    name="lastName" 
                    placeholder="Enter your last name" 
                    value={form.lastName} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 placeholder-gray-400"
                  />
                </div>
              </div>
            </div>

            {/* Contact Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number
                  </label>
                  <input 
                    name="phone" 
                    placeholder="Enter your phone number" 
                    value={form.phone} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 placeholder-gray-400"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input 
                    type="email" 
                    name="email" 
                    placeholder="Enter your email" 
                    value={form.email} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 placeholder-gray-400"
                  />
                </div>
              </div>
            </div>

            {/* Professional Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Professional Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company Name
                  </label>
                  <input 
                    name="company" 
                    placeholder="Enter your company" 
                    value={form.company} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 placeholder-gray-400"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Role
                  </label>
                  <input 
                    name="jobRole" 
                    placeholder="Enter your job role" 
                    value={form.jobRole} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 placeholder-gray-400"
                  />
                </div>
              </div>
            </div>

            {/* Account Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username
                  </label>
                  <input 
                    name="username" 
                    placeholder="Choose a username" 
                    value={form.username} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 placeholder-gray-400"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <input 
                    type="password" 
                    name="password" 
                    placeholder="Create a password" 
                    value={form.password} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 placeholder-gray-400"
                  />
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="pt-4">
              <button 
                type="submit" 
                disabled={isLoading}
                className={`w-full py-4 px-6 rounded-lg font-semibold text-white transition-all duration-200 transform ${
                  isLoading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 hover:scale-105 active:scale-95'
                } shadow-lg`}
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Creating Account...
                  </div>
                ) : (
                  'Create Account'
                )}
              </button>
            </div>

            {/* Footer */}
            <div className="text-center pt-4 border-t border-gray-200">
              <p className="text-gray-600">
                Already have an account? 
                <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium ml-1">
                  Sign in here
                </a>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}




// new2
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
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await axios.post('/api/signup', form);
      setMessage('Account created successfully! Redirecting to login...');
      setTimeout(() => {
        window.location.href = '/login';
      }, 1500);
    } catch (err) {
      setMessage('Signup failed. User may already exist.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Account</h1>
            <p className="text-gray-600">Join us today and get started</p>
          </div>

          {/* Message */}
          {message && (
            <div className={`mb-6 p-4 rounded-lg text-center ${
              message.includes('successfully') 
                ? 'bg-green-50 text-green-700 border border-green-200' 
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {message}
            </div>
          )}

          <form onSubmit={handleSignup} className="space-y-6">
            {/* Personal Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="relative">
                  <input 
                    name="firstName" 
                    placeholder=" " 
                    value={form.firstName} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 peer placeholder-transparent"
                  />
                  <label className="absolute left-4 -top-2.5 bg-white px-1 text-sm font-medium text-gray-700 transition-all duration-200 peer-placeholder-shown:top-4 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400 peer-focus:-top-2.5 peer-focus:text-sm peer-focus:text-blue-600">
                    First Name
                  </label>
                </div>
                <div className="relative">
                  <input 
                    name="lastName" 
                    placeholder=" " 
                    value={form.lastName} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 peer placeholder-transparent"
                  />
                  <label className="absolute left-4 -top-2.5 bg-white px-1 text-sm font-medium text-gray-700 transition-all duration-200 peer-placeholder-shown:top-4 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400 peer-focus:-top-2.5 peer-focus:text-sm peer-focus:text-blue-600">
                    Last Name
                  </label>
                </div>
              </div>
            </div>

            {/* Contact Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="relative">
                  <input 
                    name="phone" 
                    placeholder=" " 
                    value={form.phone} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 peer placeholder-transparent"
                  />
                  <label className="absolute left-4 -top-2.5 bg-white px-1 text-sm font-medium text-gray-700 transition-all duration-200 peer-placeholder-shown:top-4 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400 peer-focus:-top-2.5 peer-focus:text-sm peer-focus:text-blue-600">
                    Phone Number
                  </label>
                </div>
                <div className="relative">
                  <input 
                    type="email" 
                    name="email" 
                    placeholder=" " 
                    value={form.email} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 peer placeholder-transparent"
                  />
                  <label className="absolute left-4 -top-2.5 bg-white px-1 text-sm font-medium text-gray-700 transition-all duration-200 peer-placeholder-shown:top-4 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400 peer-focus:-top-2.5 peer-focus:text-sm peer-focus:text-blue-600">
                    Email Address
                  </label>
                </div>
              </div>
            </div>

            {/* Professional Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Professional Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="relative">
                  <input 
                    name="company" 
                    placeholder=" " 
                    value={form.company} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 peer placeholder-transparent"
                  />
                  <label className="absolute left-4 -top-2.5 bg-white px-1 text-sm font-medium text-gray-700 transition-all duration-200 peer-placeholder-shown:top-4 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400 peer-focus:-top-2.5 peer-focus:text-sm peer-focus:text-blue-600">
                    Company Name
                  </label>
                </div>
                <div className="relative">
                  <input 
                    name="jobRole" 
                    placeholder=" " 
                    value={form.jobRole} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 peer placeholder-transparent"
                  />
                  <label className="absolute left-4 -top-2.5 bg-white px-1 text-sm font-medium text-gray-700 transition-all duration-200 peer-placeholder-shown:top-4 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400 peer-focus:-top-2.5 peer-focus:text-sm peer-focus:text-blue-600">
                    Job Role
                  </label>
                </div>
              </div>
            </div>

            {/* Account Information */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="relative">
                  <input 
                    name="username" 
                    placeholder=" " 
                    value={form.username} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 peer placeholder-transparent"
                  />
                  <label className="absolute left-4 -top-2.5 bg-white px-1 text-sm font-medium text-gray-700 transition-all duration-200 peer-placeholder-shown:top-4 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400 peer-focus:-top-2.5 peer-focus:text-sm peer-focus:text-blue-600">
                    Username
                  </label>
                </div>
                <div className="relative">
                  <input 
                    type="password" 
                    name="password" 
                    placeholder=" " 
                    value={form.password} 
                    onChange={handleChange} 
                    required 
                    className="w-full px-4 py-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 peer placeholder-transparent"
                  />
                  <label className="absolute left-4 -top-2.5 bg-white px-1 text-sm font-medium text-gray-700 transition-all duration-200 peer-placeholder-shown:top-4 peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-400 peer-focus:-top-2.5 peer-focus:text-sm peer-focus:text-blue-600">
                    Password
                  </label>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="pt-4">
              <button 
                type="submit" 
                disabled={isLoading}
                className={`w-full py-4 px-6 rounded-lg font-semibold text-white transition-all duration-200 transform ${
                  isLoading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 hover:scale-105 active:scale-95'
                } shadow-lg`}
              >
                {isLoading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Creating Account...
                  </div>
                ) : (
                  'Create Account'
                )}
              </button>
            </div>

            {/* Footer */}
            <div className="text-center pt-4 border-t border-gray-200">
              <p className="text-gray-600">
                Already have an account? 
                <a href="/login" className="text-blue-600 hover:text-blue-700 font-medium ml-1">
                  Sign in here
                </a>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
                    }
