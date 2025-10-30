# MadeInPK Authentication API

**Base URL:** `http://localhost:8000/api/`

---

## Overview

MadeInPK uses Token-based authentication. After successful login/registration, you receive a token that must be included in the `Authorization` header for all authenticated requests.

**Header Format:**
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

---

## Register

Create a new user account.

**Endpoint:** `POST /api/auth/register/`

**Authentication:** Not required

### Request Body

```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "Ali",
  "last_name": "Raza",
  "phone_number": "+923001234567",
  "role": "buyer"
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | Unique username (3-150 chars) |
| email | string | Yes | Unique email address |
| password | string | Yes | Password (min 8 chars) |
| password_confirm | string | Yes | Must match password |
| first_name | string | No | User's first name |
| last_name | string | No | User's last name |
| phone_number | string | No | Phone number with country code |
| role | string | Yes | User role (see below) |

### Role Options

| Role | Description |
|------|-------------|
| `buyer` | Can purchase items only |
| `seller` | Can sell items only |
| `both` | Can buy and sell |
| `admin` | Administrative access |

### Success Response (201 Created)

```json
{
  "user": {
    "id": 9,
    "username": "newuser",
    "email": "newuser@example.com",
    "first_name": "Ali",
    "last_name": "Raza",
    "phone_number": "+923001234567",
    "profile_picture": null,
    "profile_picture_url": null,
    "role": "buyer",
    "is_blocked": false,
    "failed_payment_count": 0,
    "created_at": "2025-10-27T18:30:00Z"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

### Error Responses

**400 Bad Request - Validation Errors:**

```json
{
  "password": ["Passwords do not match"],
  "email": ["User with this email already exists."],
  "username": ["A user with that username already exists."]
}
```

**400 Bad Request - Password Too Short:**

```json
{
  "password": ["This password is too short. It must contain at least 8 characters."]
}
```

### cURL Example

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "Ali",
    "last_name": "Raza",
    "phone_number": "+923001234567",
    "role": "buyer"
  }'
```

### JavaScript/Axios Example

```javascript
import axios from 'axios';

async function register(userData) {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/auth/register/',
      userData
    );
    
    // Store token
    localStorage.setItem('authToken', response.data.token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    
    return response.data;
  } catch (error) {
    console.error('Registration failed:', error.response.data);
    throw error;
  }
}

// Usage
const newUser = {
  username: 'newuser',
  email: 'newuser@example.com',
  password: 'securepass123',
  password_confirm: 'securepass123',
  first_name: 'Ali',
  last_name: 'Raza',
  phone_number: '+923001234567',
  role: 'buyer'
};

register(newUser);
```

---

## Login

Authenticate existing user and receive token.

**Endpoint:** `POST /api/auth/login/`

**Authentication:** Not required

### Request Body

```json
{
  "email": "buyer1@example.com",
  "password": "password123"
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | User's email address |
| password | string | Yes | User's password |

### Success Response (200 OK)

```json
{
  "user": {
    "id": 1,
    "username": "buyer1",
    "email": "buyer1@example.com",
    "first_name": "Ahmed",
    "last_name": "Khan",
    "phone_number": "+923001234567",
    "profile_picture": null,
    "profile_picture_url": null,
    "role": "buyer",
    "is_blocked": false,
    "failed_payment_count": 0,
    "created_at": "2025-10-20T10:00:00Z"
  },
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
}
```

### Error Responses

**401 Unauthorized - Invalid Credentials:**

```json
{
  "error": "Invalid credentials"
}
```

**403 Forbidden - Account Blocked:**

```json
{
  "error": "Your account is blocked"
}
```

### cURL Example

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "buyer1@example.com",
    "password": "password123"
  }'
```

### JavaScript/Axios Example

```javascript
async function login(email, password) {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/auth/login/',
      { email, password }
    );
    
    // Store token and user data
    localStorage.setItem('authToken', response.data.token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
    
    return response.data;
  } catch (error) {
    if (error.response?.status === 401) {
      alert('Invalid email or password');
    } else if (error.response?.status === 403) {
      alert('Your account has been blocked');
    }
    throw error;
  }
}

// Usage
login('buyer1@example.com', 'password123');
```

---

## Logout

Invalidate the current authentication token.

**Endpoint:** `POST /api/auth/logout/`

**Authentication:** Required

### Request Headers

```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

### Success Response (200 OK)

```json
{
  "message": "Logged out successfully"
}
```

### Error Response

**401 Unauthorized:**

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### cURL Example

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
```

### JavaScript/Axios Example

```javascript
async function logout() {
  const token = localStorage.getItem('authToken');
  
  try {
    await axios.post(
      'http://localhost:8000/api/auth/logout/',
      {},
      {
        headers: {
          'Authorization': `Token ${token}`
        }
      }
    );
    
    // Clear local storage
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    
    // Redirect to login
    window.location.href = '/login';
  } catch (error) {
    console.error('Logout failed:', error);
  }
}
```

---

## Get Profile

Retrieve current authenticated user's profile information.

**Endpoint:** `GET /api/auth/profile/`

**Authentication:** Required

### Request Headers

```
Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
```

### Success Response (200 OK)

**For Buyer:**

```json
{
  "id": 1,
  "username": "buyer1",
  "email": "buyer1@example.com",
  "first_name": "Ahmed",
  "last_name": "Khan",
  "phone_number": "+923001234567",
  "profile_picture": null,
  "profile_picture_url": null,
  "role": "buyer",
  "created_at": "2025-10-20T10:00:00Z",
  "total_sales": 0,
  "total_purchases": 5,
  "average_seller_rating": null,
  "seller_profile": null
}
```

**For Seller:**

```json
{
  "id": 5,
  "username": "seller1",
  "email": "seller1@example.com",
  "first_name": "Hassan",
  "last_name": "Textiles",
  "phone_number": "+923041234567",
  "profile_picture": null,
  "profile_picture_url": null,
  "role": "seller",
  "created_at": "2025-10-20T10:00:00Z",
  "total_sales": 15,
  "total_purchases": 3,
  "average_seller_rating": 4.7,
  "seller_profile": {
    "id": 1,
    "user": 5,
    "user_username": "seller1",
    "user_email": "seller1@example.com",
    "brand_name": "Hassan Textiles",
    "biography": "Family-owned textile business for 3 generations, specializing in handwoven fabrics.",
    "business_address": "123 Textile Market, Faisalabad, Punjab",
    "website": "https://hassantextiles.pk",
    "social_media_links": {},
    "is_verified": true,
    "average_rating": "4.70",
    "total_feedbacks": 12,
    "created_at": "2025-10-20T10:00:00Z",
    "updated_at": "2025-10-27T15:30:00Z"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| id | integer | User ID |
| username | string | Username |
| email | string | Email address |
| first_name | string | First name |
| last_name | string | Last name |
| phone_number | string | Phone number |
| profile_picture | string | Profile picture path (if uploaded) |
| profile_picture_url | string | Full URL to profile picture |
| role | string | User role (buyer/seller/both/admin) |
| created_at | datetime | Account creation timestamp |
| total_sales | integer | Number of completed sales (for sellers) |
| total_purchases | integer | Number of completed purchases |
| average_seller_rating | float | Average rating as seller (null if not seller) |
| seller_profile | object | Seller profile details (null if not seller) |

### cURL Example

```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0"
```

### JavaScript/Axios Example

```javascript
async function getProfile() {
  const token = localStorage.getItem('authToken');
  
  try {
    const response = await axios.get(
      'http://localhost:8000/api/auth/profile/',
      {
        headers: {
          'Authorization': `Token ${token}`
        }
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('Failed to fetch profile:', error);
    throw error;
  }
}

// Usage
getProfile().then(profile => {
  console.log('User profile:', profile);
});
```

---

## React Authentication Context Example

Here's a complete authentication context for React applications:

```javascript
import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    const storedToken = localStorage.getItem('authToken');
    const storedUser = localStorage.getItem('user');
    
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      
      // Set default axios header
      axios.defaults.headers.common['Authorization'] = `Token ${storedToken}`;
    }
    
    setLoading(false);
  }, []);

  // Register function
  const register = async (userData) => {
    try {
      const response = await axios.post(
        'http://localhost:8000/api/auth/register/',
        userData
      );
      
      const { user, token } = response.data;
      
      // Save to state and localStorage
      setUser(user);
      setToken(token);
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Set default axios header
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
      
      return { success: true, user };
    } catch (error) {
      return { 
        success: false, 
        errors: error.response?.data || { message: 'Registration failed' }
      };
    }
  };

  // Login function
  const login = async (email, password) => {
    try {
      const response = await axios.post(
        'http://localhost:8000/api/auth/login/',
        { email, password }
      );
      
      const { user, token } = response.data;
      
      // Save to state and localStorage
      setUser(user);
      setToken(token);
      localStorage.setItem('authToken', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Set default axios header
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
      
      return { success: true, user };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Login failed'
      };
    }
  };

  // Logout function
  const logout = async () => {
    try {
      await axios.post('http://localhost:8000/api/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear state and localStorage regardless of API response
      setUser(null);
      setToken(null);
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  // Refresh profile
  const refreshProfile = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/auth/profile/');
      setUser(response.data);
      localStorage.setItem('user', JSON.stringify(response.data));
      return response.data;
    } catch (error) {
      console.error('Failed to refresh profile:', error);
      return null;
    }
  };

  const value = {
    user,
    token,
    loading,
    isAuthenticated: !!token,
    isSeller: user?.role === 'seller' || user?.role === 'both',
    isBuyer: user?.role === 'buyer' || user?.role === 'both',
    isAdmin: user?.role === 'admin',
    register,
    login,
    logout,
    refreshProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
```

### Usage in Components

```javascript
import { useAuth } from './contexts/AuthContext';

function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(email, password);
    
    if (result.success) {
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } else {
      setError(result.error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error">{error}</div>}
      <input 
        type="email" 
        value={email} 
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required 
      />
      <input 
        type="password" 
        value={password} 
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required 
      />
      <button type="submit">Login</button>
    </form>
  );
}

function ProtectedComponent() {
  const { isAuthenticated, user, isSeller } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  return (
    <div>
      <h1>Welcome, {user.username}!</h1>
      {isSeller && <p>You can create listings</p>}
    </div>
  );
}
```

---

## Sample Test Users

Use these accounts for testing (password: `password123` for all):

| Username | Email | Role | Description |
|----------|-------|------|-------------|
| buyer1 | buyer1@example.com | buyer | Regular buyer account |
| buyer2 | buyer2@example.com | buyer | Regular buyer account |
| buyer3 | buyer3@example.com | buyer | Regular buyer account |
| seller1 | seller1@example.com | seller | Verified seller (Hassan Textiles) |
| seller2 | seller2@example.com | seller | Verified seller (Ayesha Crafts) |
| seller3 | seller3@example.com | seller | Unverified seller (Ahmed Pottery) |
| seller4 | seller4@example.com | both | Can buy and sell (Zara Jewelry) |
| buyer_seller1 | buyer_seller1@example.com | both | Can buy and sell |

---

## Security Best Practices

### 1. Store Tokens Securely

```javascript
// ✅ Good: Use httpOnly cookies (if backend supports)
// ✅ Acceptable: localStorage for development
localStorage.setItem('authToken', token);

// ❌ Bad: Don't expose tokens in URLs
// Don't do: /dashboard?token=abc123
```

### 2. Handle Token Expiration

```javascript
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 3. Validate User Input

```javascript
function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function validatePassword(password) {
  return password.length >= 8;
}
```

### 4. Use HTTPS in Production

```javascript
const API_URL = process.env.NODE_ENV === 'production'
  ? 'https://api.madeinpk.com'
  : 'http://localhost:8000';
```

---

**End of Authentication API Documentation**
