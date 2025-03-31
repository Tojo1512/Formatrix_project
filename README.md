# Formatrix - Training Management System

Formatrix is a comprehensive training management system designed to streamline the process of organizing, scheduling, and managing training sessions, instructors, students, and course materials.

## Features

### Course Management
- Create and manage detailed course profiles with objectives, prerequisites, and material requirements
- Set course duration, pricing, and approval status
- Assign instructors to courses
- Track course validity and expiration dates
- Manage course versions and updates

### Session Scheduling
- Schedule training sessions with specific dates and locations
- Assign multiple instructors to sessions
- Track session status (not started, in progress, completed, cancelled)
- Manage session capacity and attendance
- Handle instructor absences and replacements

### Student Management
- Register students with comprehensive profiles (personal information, contact details)
- Track academic levels and special needs
- Categorize students by age groups and educational background
- Associate students with client organizations
- Record emergency contact information

### Instructor Management
- Manage detailed instructor profiles with expertise levels and specializations
- Track instructor availability and schedule
- Upload instructor CV and photos
- Monitor instructor performance
- Categorize instructors by type (internal, external, consultant)

### Client Management
- Register client organizations
- Track client contact information
- Manage client-specific training requirements
- Associate students with client organizations

### Attendance & Evaluation
- Record and monitor student attendance
- Create and manage evaluations for students
- Generate attendance reports
- Track student progress throughout the course

### Reporting System
- Generate detailed reports on various aspects of the training program
- Visualize key metrics on the dashboard
- Export reports in different formats
- Monitor training program performance

### Payment Management
- Track payments for courses and training sessions
- Generate invoices
- Monitor payment status

## Technology Stack

- Django 4.2+
- Django REST Framework
- SQLite (for local development)
- Bootstrap (frontend)
- HTML/CSS/JavaScript

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Basic Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/formatrix.git
   cd formatrix
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Navigate to the project directory:
   ```
   cd formatrix
   ```

6. Apply migrations:
   ```
   python manage.py migrate
   ```

7. Create a superuser (admin):
   ```
   python manage.py createsuperuser
   ```

8. Run the development server:
   ```
   python manage.py runserver
   ```

9. Access the application at http://127.0.0.1:8000/

## Network Setup (Local Multi-Computer Use)

To use Formatrix on multiple computers within a local network with one computer acting as the server:

### Server Computer Setup

1. Follow the basic setup instructions above
2. Identify your server's IP address:
   - Windows: Open Command Prompt and type `ipconfig`
   - macOS/Linux: Open Terminal and type `ifconfig` or `ip addr`
   - Note down the IPv4 address (typically starts with 192.168.x.x or 10.x.x.x)

3. Run the development server and make it accessible on the network:
   ```
   python manage.py runserver 0.0.0.0:8000
   ```
   
   This will make the server listen on all network interfaces, not just localhost.

4. Ensure your firewall allows connections on port 8000

### Client Computer Access

1. On any other computer in the same network, open a web browser
2. Enter the server's IP address followed by the port:
   ```
   http://SERVER_IP:8000/
   ```
   Replace SERVER_IP with the actual IP address of the server computer (e.g., http://192.168.1.100:8000/)

3. You can now access and use the Formatrix system from the client computer

### Network Security Considerations (Optional)

- For a more secure setup, consider using HTTPS even on a local network
- You can set up a basic HTTPS server using Django's development server and a self-signed certificate
- Restrict access to sensitive admin functions by IP address
- Configure proper user permissions for different staff roles

## Usage Guide

### Initial Setup

1. **Register as Admin**:
   - Go to http://SERVER_IP:8000/admin-register/
   - Use the admin registration code: `admin_secret_code_2024` (found in `settings.py`)
   - Complete the registration form with your details

2. **Create Training Locations**:
   - Navigate to the Locations module
   - Add your training locations with address and capacity details

3. **Set Up Courses**:
   - Go to the Courses module
   - Create course profiles with all necessary details
   - Set approval status for courses

### Managing Trainers

1. **Trainer Registration**:
   - Trainers can register at http://SERVER_IP:8000/register/
   - They'll need the trainer registration key: `formateur_secret_key_2024` (found in `settings.py`)

2. **Review and Approve Trainers**:
   - Admin can review trainer profiles
   - Assign specialties and expertise levels
   - Set availability status

3. **Assign Trainers to Courses**:
   - Select courses in the course management section
   - Add authorized trainers to specific courses

### Creating and Managing Sessions

1. **Schedule New Sessions**:
   - Go to the Sessions module
   - Select the course, dates, and location
   - Assign one or more trainers
   - Set capacity and pricing

2. **Managing Session Status**:
   - Update session status as it progresses
   - Record attendance for each session
   - Handle trainer absences and replacements

### Student Registration and Management

1. **Add New Students**:
   - Register students with all required details
   - Associate them with client organizations if applicable
   - Record special needs or requirements

2. **Enrolling Students**:
   - Add students to specific sessions
   - Track enrollment status
   - Record payments

3. **Attendance and Evaluation**:
   - Take attendance for each session
   - Record student evaluations
   - Generate progress reports

### Reports and Analytics

1. **Dashboard Overview**:
   - View key metrics on the home dashboard
   - Monitor upcoming sessions
   - Track trainer activity

2. **Generating Reports**:
   - Access the Reports module
   - Select report type and parameters
   - Export or print reports as needed

## Project Structure

The project is organized into multiple Django apps:

- `cours`: Course management
- `seances`: Session scheduling and management
- `apprenants`: Student management
- `formateurs`: Trainer management
- `clients`: Client organization management
- `inscriptions`: Registration management
- `presences`: Attendance tracking
- `lieux`: Location management
- `paiements`: Payment tracking
- `evaluations`: Evaluation management
- `rapports`: Reporting system
- `notifications`: Notification system

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributors

- Your Name
- Other Contributors

---

For any questions or support, please contact support@formatrix.com 