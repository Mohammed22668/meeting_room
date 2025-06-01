# 🏢 Meeting Room Booking System

A web-based system built with Django for managing booking requests for a meeting room, including request submission, admin approval, and status tracking. Designed with Bootstrap for a clean and responsive user interface.

---

## 📌 Features

- 🎯 **Landing Page**: Welcome page with an overview and navigation links.
- 📝 **Booking Form**: Public users can request a booking without registration.
- 📄 **Booking Reference ID**: A unique request number is displayed upon submission.
- 🔍 **Track Request**: Users can check the status of their request using the reference ID.
- 🔐 **Admin Panel**: (Optional in future stages) Super admin can approve/reject requests.

---

## 📷 Screenshots

> 💡 Add screenshots of the homepage, booking form, and status tracking page here.

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/Mohammed22668/meeting_room.git
cd meeting-room-booking


```

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

```bash
python manage.py migrate
```

```bash
python manage.py runserver
```
