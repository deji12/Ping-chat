# ping · real‑time chat platform

**ping** is a modern, full‑featured chat application that combines a clean user interface with real‑time messaging. Built with Django, Django Channels (WebSockets), Bootstrap 5, and a custom purple‑blue design system. It supports user authentication, friend management, one‑on‑one chats, image messages, and real‑time updates.

![ping chat preview](https://via.placeholder.com/800x400?text=ping+chat+screenshot)

---

## ✨ Features

- **User accounts** – register, login, password reset (with email simulation).
- **Profile management** – edit personal info, bio, profile picture, change password.
- **Friend system** – send/accept/decline friend requests, view friend list, mutual friends.
- **Real‑time chat** – one‑on‑one conversations with WebSockets (Django Channels).
- **Rich messages** – send text and images (with preview & caption, like WhatsApp).
- **Responsive UI** – fully mobile‑friendly, works on desktop, tablet, and phone.
- **Modern design** – custom purple/blue gradient, rounded cards, smooth animations.
- **Search & discover** – find other users by name or username.
- **Unread indicators** – see pending messages at a glance.
- **Friends since** – track when you became friends with someone.

---

## 🛠 Tech Stack

| Category         | Technology                                                                 |
|------------------|----------------------------------------------------------------------------|
| Backend          | Django 5.x, Django Channels (WebSockets)                                   |
| Database         | PostgreSQL (or SQLite for development)                                    |
| Real‑time        | ASGI, WebSocket consumer, In‑memory channel layer (Redis for production)  |
| Frontend         | Bootstrap 5, Bootstrap Icons, Inter font, custom CSS                       |
| JavaScript       | Vanilla JS (WebSocket client, dynamic UI updates)                         |
| Media storage    | Cloudinary (for images)                                                   |
| Authentication   | Django’s built‑in auth + custom `LoginRequiredMixin`                      |

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js (optional – for frontend tooling, not required)
- PostgreSQL (or SQLite)

### 1. Clone the repository
```bash
git clone https://github.com/deji12/ping.git
cd ping
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
Create a `.env` file in the project root:
```env
SECRET_KEY=key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
DEFAULT_USER_PROFILE_IMAGE=https://res.cloudinary.com/the-proton-guy/image/upload/v1660906962/6215195_0_pjwqfq.webp
EMAIL_HOST=
EMAIL_PORT=
EMAIL_USE_SSL=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Start the development server
```bash
python manage.py runserver
```