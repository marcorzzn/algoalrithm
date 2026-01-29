# Football Analytics API Documentation

## Authentication
All endpoints except `/health` and `/auth/login` require JWT token.

**Header:** `Authorization: Bearer &lt;token&gt;`

## Endpoints

### POST /api/auth/register
Register new user.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}