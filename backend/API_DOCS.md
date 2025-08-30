# Hotel Management API Documentation

## Overview

This API provides comprehensive hotel management functionality including user authentication, hotel and room management, customer profiles, and reservation systems.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### Get JWT Token

**POST** `/api/token/`

**Request Body:**
```json
{
    "email": "user@example.com",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Refresh Token

**POST** `/api/token/refresh/`

**Request Body:**
```json
{
    "refresh": "your_refresh_token"
}
```

## Users

### List Users

**GET** `/api/users/`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "email": "user@example.com",
            "name": "John Doe",
            "phone": "+1234567890",
            "is_customer": true,
            "is_employer": false
        }
    ]
}
```

### Create User

**POST** `/api/users/`

**Request Body:**
```json
{
    "email": "newuser@example.com",
    "password": "secure_password",
    "name": "Jane Doe",
    "phone": "+1234567890",
    "is_customer": true
}
```

### Get User Details

**GET** `/api/users/{id}/`

### Update User

**PUT** `/api/users/{id}/`

### Delete User

**DELETE** `/api/users/{id}/`

## Hotels

### List Hotels

**GET** `/api/hotels/`

**Response:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Grand Hotel",
            "email": "info@grandhotel.com",
            "phone": "+1234567890",
            "street": "123 Main St",
            "number": "100",
            "complement": "Downtown",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "website": "https://grandhotel.com"
        }
    ]
}
```

### Create Hotel

**POST** `/api/hotels/`

**Request Body:**
```json
{
    "name": "New Hotel",
    "email": "info@newhotel.com",
    "phone": "+1234567890",
    "street": "456 Oak Ave",
    "number": "200",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90210"
}
```

## Rooms

### List Rooms

**GET** `/api/rooms/`

**Response:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "hotel": 1,
            "number": 101,
            "complement": "Deluxe Suite",
            "is_available": true
        }
    ]
}
```

### Create Room

**POST** `/api/rooms/`

**Request Body:**
```json
{
    "hotel": 1,
    "number": 102,
    "complement": "Standard Room"
}
```

## Reservations

### List Reservations

**GET** `/api/reservations/`

**Response:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "customer": {
                "id": 1,
                "user": {
                    "id": 1,
                    "email": "customer@example.com",
                    "name": "John Doe"
                }
            },
            "room": {
                "id": 1,
                "number": 101,
                "hotel": "Grand Hotel"
            },
            "check_in": "2024-01-15",
            "check_out": "2024-01-17",
            "booking_status": "Confirmed"
        }
    ]
}
```

### Create Reservation

**POST** `/api/reservations/`

**Request Body:**
```json
{
    "room_id": 1,
    "customer_id": 1,
    "check_in": "2024-01-15",
    "check_out": "2024-01-17",
    "booking_status": "Confirmed"
}
```

**Validation Rules:**
- `check_out` must be after `check_in`
- Room must be available
- No conflicting reservations for the same room and dates

### Update Reservation

**PUT** `/api/reservations/{id}/`

### Cancel Reservation

**PUT** `/api/reservations/{id}/`

**Request Body:**
```json
{
    "booking_status": "Cancelled"
}
```

## Customers

### List Customers

**GET** `/api/customers/`

**Response:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "user": {
                "id": 1,
                "email": "customer@example.com",
                "name": "John Doe",
                "phone": "+1234567890"
            },
            "preferences": {
                "room_type": "non-smoking",
                "floor": "high"
            }
        }
    ]
}
```

### Create Customer

**POST** `/api/customers/`

**Request Body:**
```json
{
    "user": {
        "email": "newcustomer@example.com",
        "password": "secure_password",
        "name": "Jane Doe",
        "phone": "+1234567890"
    },
    "preferences": {
        "room_type": "non-smoking",
        "floor": "high"
    }
}
```

## Employers

### List Employers

**GET** `/api/employers/`

### Create Employer

**POST** `/api/employers/`

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Error Responses

**Example Error Response:**
```json
{
    "error": "Validation failed",
    "details": {
        "check_out": ["check_out must be after check_in."]
    }
}
```

## Pagination

All list endpoints support pagination with the following parameters:

- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

## Filtering and Search

### Reservations
- Filter by status: `/api/reservations/?booking_status=Confirmed`
- Filter by date range: `/api/reservations/?check_in__gte=2024-01-01&check_out__lte=2024-01-31`

### Rooms
- Filter by availability: `/api/rooms/?is_available=true`
- Filter by hotel: `/api/rooms/?hotel=1`

### Customers
- Search by name: `/api/customers/?user__name__icontains=john`

## Background Tasks

### Email Notifications
- Confirmation emails are sent automatically when reservations are confirmed
- Emails are sent asynchronously via Celery

### Room Cleanup
- Automatic room availability updates every 10 minutes
- Rooms are marked as available after check-out dates

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Security Considerations

- Use HTTPS in production
- Implement proper CORS policies
- Consider API key authentication for external integrations
- Validate all input data
- Use environment variables for sensitive configuration

## Development

### Local Development
1. Start Redis server
2. Start Celery worker: `celery -A project worker --loglevel=info`
3. Start Celery beat: `celery -A project beat --loglevel=info`
4. Start Django server: `python manage.py runserver`

### Testing
```bash
python manage.py test
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Support

For questions or issues, please contact the development team or create an issue in the project repository.
