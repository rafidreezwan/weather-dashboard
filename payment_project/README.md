# Django aamarPay File Upload System

This project is a Django application that allows users to upload files after completing a payment via the aamarPay sandbox. It uses Celery and Redis for background processing.

## Setup and Installation

1.  **Prerequisites:**
    * Python 3.x
    * Git
    * Redis (for Windows, install from [here](https://github.com/microsoftarchive/redis/releases))

2.  **Clone the repository:**
    ```bash
    git clone [https://github.com/rafidreezwan/Django-Payment-Gateway.git](https://github.com/rafidreezwan/Django-Payment-Gateway.git)
    cd Django-Payment-Gateway
    ```

3.  **Set up virtual environment and install dependencies:**
    ```bash
    # For Windows
    py -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

4.  **Apply migrations and create a superuser:**
    ```bash
    py manage.py migrate
    py manage.py createsuperuser
    ```

5.  **Run the application:**
    * **Terminal 1 (Celery Worker):**
        ```bash
        # On Windows, ensure Redis service is running
        celery -A core worker -l info -P eventlet
        ```
    * **Terminal 2 (Django Server):**
        ```bash
        py manage.py runserver
        ```

6.  Access the application at `http://127.0.0.1:8000/dashboard/`.

## How to Test the Payment Flow

1.  Log in via the admin panel: `http://127.0.0.1:8000/admin/`.
2.  Navigate to the dashboard: `http://127.0.0.1:8000/dashboard/`.
3.  Click "Pay Now."
4.  On the aamarPay page, click the green "Success" button.
5.  You will be returned to the dashboard where you can now upload a file.