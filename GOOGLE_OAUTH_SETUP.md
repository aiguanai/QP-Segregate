# Google OAuth Setup Guide

This guide explains how to set up Google OAuth authentication for student login.

## Overview

Students can now log in using their Google accounts. The system automatically:
- Validates that the email is from `@rvce.edu.in` domain
- Creates a new user account if it doesn't exist
- Blocks access for non-RVCE email addresses

## Backend Setup

### 1. Install Dependencies

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

This will install:
- `google-auth==2.23.4`
- `google-auth-oauthlib==1.1.0`
- `google-auth-httplib2==0.1.1`

### 2. Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google+ API** (or **Google Identity API**)
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Choose **Web application**
6. Add authorized JavaScript origins:
   - `http://localhost:3000` (for development)
   - `https://yourdomain.com` (for production)
7. Add authorized redirect URIs:
   - `http://localhost:3000` (for development)
   - `https://yourdomain.com` (for production)
8. Copy the **Client ID** and **Client Secret**

### 3. Update Environment Variables

Add to `backend/.env`:

```env
# Google OAuth (for student login)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

**Note:** The backend doesn't actually need the client secret for token verification (it uses Google's public tokeninfo endpoint), but it's included for future use.

## Frontend Setup

### 1. Install Dependencies

```powershell
cd frontend
npm install @react-oauth/google
```

### 2. Get Google OAuth Client ID

Use the same Client ID from the backend setup.

### 3. Update Environment Variables

Create `frontend/.env.local`:

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Google OAuth Client ID (for student login)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
```

### 4. Restart Frontend

After adding the environment variable, restart the Next.js dev server:

```powershell
npm run dev
```

## How It Works

1. **Student clicks "Sign in with Google"** on the login page
2. **Google OAuth popup** appears for authentication
3. **User selects their Google account** (must be @rvce.edu.in)
4. **Frontend receives Google token** and sends it to backend `/api/auth/google-login`
5. **Backend verifies token** with Google's API
6. **Backend validates email domain** - must be @rvce.edu.in
7. **Backend creates/updates user** in database
8. **Backend returns JWT token** to frontend
9. **Frontend stores token** and redirects to dashboard

## Security Features

- ✅ **Domain Restriction**: Only @rvce.edu.in emails are allowed
- ✅ **Token Verification**: Google tokens are verified server-side
- ✅ **Automatic User Creation**: New students are automatically registered
- ✅ **No Passwords**: Students don't need passwords (OAuth only)

## Testing

1. Go to http://localhost:3000/student/login
2. Click "Sign in with Google"
3. Select a Google account with @rvce.edu.in email
4. You should be redirected to the student dashboard

**Note:** If you test with a non-RVCE email, you'll get an error: "Access restricted to @rvce.edu.in email addresses only"

## Troubleshooting

### "Invalid Google token" error
- Check that your Google Client ID is correct
- Make sure `http://localhost:3000` is in authorized JavaScript origins

### "Access restricted" error
- The email must end with `@rvce.edu.in`
- Check that you're using an RVCE Google account

### Google Sign-In button not appearing
- Check browser console for errors
- Verify `NEXT_PUBLIC_GOOGLE_CLIENT_ID` is set correctly
- Restart the Next.js dev server after adding the env variable

## Admin Login

Admin login remains unchanged - still uses username/password:
- Username: `admin`
- Password: `admin123`

