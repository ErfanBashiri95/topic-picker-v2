
# 🪐 Topic Choose App — A Smart Topic Selection System

A web-based application built with **Flask (Python)** that enables course participants to log in, view a list of training topics, and select their preferred ones — while automatically locking topics chosen by others in real-time.  

This project was originally developed for the **Nil Coaching Academy**, used in the *Helix Coaching Program* to streamline topic assignments during professional coaching sessions.

---

## 🚀 Features

✅ **User Login System** — Each participant logs in with their name and a preset username (no registration needed).  
✅ **Topic Locking Mechanism** — Once a topic is selected, it becomes locked (marked in red 🔒) to prevent duplicate selection.  
✅ **Admin Dashboard** — Secure admin panel with:
- Downloadable CSV of all selections
- Printable overview (for session reports)
- 🔄 One-click "Reset All" button to clear all data
✅ **Responsive Design** — Fully optimized for desktop and mobile screens.  
✅ **Visual Identity** — Integrated Nil Coaching logo on every page, fixed to the bottom-right corner for consistent branding.  

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-------------|
| Backend | Python Flask |
| Frontend | HTML5, CSS3 (Tailwind-inspired custom styles) |
| Data Storage | JSON-based local storage (`users.json`, `topics.json`) |
| Deployment | Render.com |
| Version Control | Git & GitHub |

---

## 🛠️ Project Structure

├── app.py # Main Flask application ├── data/ │ ├── users.json # List of authorized participants │ └── topics.json # List of topics and chosen users ├── templates/ │ ├── login.html # Login page │ ├── topics.html # Participant topic selection page │ ├── admin_dashboard.html # Admin control panel ├── static/ │ ├── style.css # Global styling │ └── images/logo.png # Nil Coaching logo └── requirements.txt # Dependencies (Flask, Gunicorn)

---

## 👨‍💻 Developer

**Erfan Bashiri** — Full-stack developer & creative systems designer.  
Focus areas:  
- Python & Flask applications  
- Interactive web systems  
- Creative design & motion for education/learning platforms  

> 🌐 Part of the **Nil Coaching Academy** technology ecosystem.

---

## 📬 Contact

If you’d like to collaborate, improve, or adapt this system for your team, feel free to reach out:

**📧** erfanbashiri28@gmail.com  
**💼** [GitHub Profile](https://github.com/ErfanBashiri95)

---

### ⭐ Show your support
If you liked this project, give it a ⭐ on GitHub — it helps others find it too!


---
