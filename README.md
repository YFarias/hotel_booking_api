# Hotel Management API

A Django-based REST API for managing hotels, rooms, customers, and reservations with authentication, background tasks, and SQLite database support.

## Features

- **User Management**: Custom user model with JWT authentication
- **Hotel Management**: CRUD operations for hotels and rooms
- **Customer Management**: Customer profiles and management
- **Reservation System**: Booking management with status tracking
- **Background Tasks**: Celery integration for email notifications and room cleanup
- **REST API**: Full REST API with Django REST Framework
- **Admin Interface**: Django admin for data management

## Project Structure

```
backend/
├── project/          # Main Django project settings
├── users/           # User authentication and management
├── customers/       # Customer profiles and management
├── hotels/          # Hotel information management
├── rooms/           # Room management and availability
├── reservations/    # Booking and reservation system
├── employers/       # Staff and employee management
└── core/           # Shared utilities and permissions
```

## Technology Stack

- **Backend**: Django 4.2.23
- **API**: Django REST Framework
- **Authentication**: JWT (Simple JWT)
- **Database**: SQLite (development)
- **Background Tasks**: Celery with Redis
- **Task Scheduling**: django-celery-beat

## Setup Instructions

### Prerequisites

- Python 3.8+
- Redis server
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hotel_api
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Set up Redis**
   - Install Redis server
   - Start Redis service
   - Default configuration: `redis://localhost:6379/0`

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Celery worker**
   ```bash
   celery -A project worker --loglevel=info
   ```

8. **Start Celery beat (scheduler)**
   ```bash
   celery -A project beat --loglevel=info
   ```

9. **Run development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Users
- `GET /api/users/` - List users
- `POST /api/users/` - Create user
- `GET /api/users/{id}/` - Get user details
- `PUT /api/users/{id}/` - Update user
- `DELETE /api/users/{id}/` - Delete user

### Hotels
- `GET /api/hotels/` - List hotels
- `POST /api/hotels/` - Create hotel
- `GET /api/hotels/{id}/` - Get hotel details
- `PUT /api/hotels/{id}/` - Update hotel
- `DELETE /api/hotels/{id}/` - Delete hotel

### Rooms
- `GET /api/rooms/` - List rooms
- `POST /api/rooms/` - Create room
- `GET /api/rooms/{id}/` - Get room details
- `PUT /api/rooms/{id}/` - Update room
- `DELETE /api/rooms/{id}/` - Delete room

### Reservations
- `GET /api/reservations/` - List reservations
- `POST /api/reservations/` - Create reservation
- `GET /api/reservations/{id}/` - Get reservation details
- `PUT /api/reservations/{id}/` - Update reservation
- `DELETE /api/reservations/{id}/` - Delete reservation

### Customers
- `GET /api/customers/` - List customers
- `POST /api/customers/` - Create customer
- `GET /api/customers/{id}/` - Get customer details
- `PUT /api/customers/{id}/` - Update customer
- `DELETE /api/customers/{id}/` - Delete customer

## Background Tasks

### Celery Tasks
- **Email Notifications**: Asynchronous email sending
- **Room Cleanup**: Automatic room availability updates every 10 minutes

### Task Scheduling
- Room release task runs every 10 minutes via cron

## Email Configuration

### Development
- Emails are printed to console
- No external SMTP required

### Production
- Configure SMTP settings in `project/settings.py`
- Update `EMAIL_HOST`, `EMAIL_HOST_USER`, and `EMAIL_HOST_PASSWORD`
- Recommended: Use environment variables for sensitive data

## Database Models

### Key Models
- **User**: Custom user model with email authentication
- **Hotel**: Hotel information and details
- **Room**: Room details with availability status
- **Customer**: Customer profiles and information
- **Reservation**: Booking information with status tracking
- **Employer**: Staff and employee management

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
- Follow Django coding standards
- Use type hints where appropriate
- Write docstrings for functions and classes

### Environment Variables
Create a `.env` file for sensitive configuration:
```env
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Production Deployment

### Considerations
- Use PostgreSQL or MySQL instead of SQLite
- Configure proper email backend
- Set up Redis for Celery
- Use environment variables for secrets
- Configure static file serving
- Set up proper logging

### Environment Variables
```env
DEBUG=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=your-database-url
REDIS_URL=your-redis-url
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or issues, please open an issue on the repository.