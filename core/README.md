# IMAGES APP

This API allows users to upload, list, and access images based on their account tier privileges.

## Main Features

- Image Upload: Any user can upload images in PNG or JPG format via an HTTP request.
- List Images: Users can list the images they have uploaded.
- Account Tiers:
  - Basic:
    - Link to a thumbnail that's 200px in height.
  - Premium:
    - Links to thumbnails (200px and 400px in height).
    - Link to the originally uploaded image.
  - Enterprise:
    - Links to thumbnails (200px and 400px in height).
    - Link to the originally uploaded image.
    - Ability to fetch an expiring link to the image.
  - Admin Custom Tiers: 
    - Admins can create custom account tiers with configurable thumbnail sizes, links to original images, and expiring links.

## Setup & Execution:

### Using Docker (Recommended):
1. Start the services:
   - Ensure Docker is installed.
   - From the project root, run:
    ```bash
    docker-compose build
    docker-compose up
    ```  
2. Database setup:
   - Run migrations:
   ```bash
   docker-compose exec app python manage.py migrate 
   ```
   - Populate the database with initial data:
   ```bash
   docker-compose exec app python manage.py loaddata initial_data.json 
   ```
3. Access the Application:
   - You can now access the Django application at http://localhost:8000/
   - Created admin account credentials: 
   ```
   email: admin@ap.pl
   password: admin
   ```

### Traditional Setup:
- Install required packages: pip install -r requirements.txt
- Run migrations: python manage.py migrate
- Populate database with initial data: python manage.py loaddata initial_data.json
- Start the server: python manage.py runserver

## Using the API:
- Admin Panel:
  - Access the Django admin panel at: http://localhost:8000/admin/
  - Create users and assign them to different account tiers.
- Browsable API:
  - Access the DRF browsable API at: http://localhost:8000/api/
  - From here, you can upload images, list images, and access links based on user privileges.

## Tests:
- To run tests:
```bash
  docker-compose exec app python manage.py test
```
