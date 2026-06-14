# 🏨 GrandStay Hotel Booking System

> **Course:** IKB21503 Secure Software Development  
> **Campus:** UniKL MIIT  
> **Framework:** Django 5.2 (Python)  
> **Security Standards:** OWASP Top 10 · OWASP ASVS · SSDF  

---

## 📋 Project Description

GrandStay is a secure hotel room booking web application built using Django. The system allows guests to browse and reserve hotel rooms, while administrators can manage reservations, rooms, and monitor security events through an audit log.

The application implements security controls aligned with OWASP Top 10, OWASP ASVS, and Secure Software Development Framework (SSDF) standards.

---

## 👥 Team Members

| Member | Role | GitHub Username |
|--------|------|----------------|
| Member 1 | Code Development — Functional CRUD | irfan2402 |
| Member 2 | Security Testing — ZAP, Bandit, Penetration Test | |
| Member 3 | Mitigation — OWASP Controls, Code Review Checklist | |
| Member 4 | CI/CD — GitHub Repository Management | |

---

## 🔐 Security Features

| # | Security Control | Implementation | OWASP Reference |
|---|-----------------|----------------|-----------------|
| 1 | Input Validation | Whitelist regex on all form fields | ASVS V5 / A03 |
| 2 | Password Hashing | bcrypt (BCryptSHA256PasswordHasher) | ASVS V2.4 |
| 3 | Brute Force Protection | django-axes — lock after 5 failed attempts | ASVS V2.2 |
| 4 | CSRF Protection | Django CsrfViewMiddleware + tokens on all forms | ASVS V4.2 |
| 5 | Access Control (RBAC) | Role-based views — Admin and Guest roles | ASVS V4 / A01 |
| 6 | IDOR Prevention | Ownership filter on all reservation queries | A01 |
| 7 | Session Management | 30-minute timeout, HttpOnly, SameSite=Lax | ASVS V3 |
| 8 | Error Handling | Custom 400/403/404/500 pages — no stack traces | ASVS V7.4 |
| 9 | Security Headers | CSP, X-Frame-Options DENY, X-Content-Type-Options | ASVS V14.4 |
| 10 | XSS Prevention | Django template auto-escaping on all {{ variables }} | ASVS V5 / A03 |
| 11 | SQL Injection Free | Django ORM only — zero raw SQL queries | A03 |
| 12 | Audit Logging | AuditLog model + rotating security.log — no passwords logged | ASVS V7.2 |
| 13 | Configuration Security | Secrets in .env file, DEBUG=False in production | ASVS V14 |
| 14 | Dependency Management | Updated packages, Snyk SCA — 0 vulnerabilities found | ASVS V14.2 |
| 15 | Live Password Checker | Real-time strength bar + toggle show/hide on register | ASVS V2.1 |

---

## ⚙️ Installation Steps

### Prerequisites

- Python 3.10 or higher
- pip
- Git

### Setup

**1. Clone the repository**
```bash
git clone https://github.com/irfan2402/Grandstay-hotel.git
cd Grandstay-hotel
```

**2. Create virtual environment**
```bash
python -m venv venv
```

**3. Activate virtual environment**
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

**5. Configure environment**
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` and change `SECRET_KEY` to a long random string.

**6. Run database migrations**
```bash
python manage.py migrate
```

**7. Create demo accounts and sample data**
```bash
python setup_demo.py
```

**8. Start the server**
```bash
python manage.py runserver
```

**9. Open in browser**

```http://127.0.0.1:8000```

---

## 🔑 Demo Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `Admin@12345` |
| Guest | `guest1` | `Guest@12345` |

---

## 🚀 How to Run the App

Every time you want to start the app:

```bash
# Step 1 - Activate venv
venv\Scripts\activate

# Step 2 - Run server
python manage.py runserver

# Step 3 - Open browser
# Go to http://127.0.0.1:8000
```

---

## 📦 Dependencies

```Django==5.2.2

django-axes==8.3.1

bcrypt==4.2.1

python-dotenv==1.2.2

Pillow==11.2.1

---

## 📁 Project Structure

Grandstay-hotel/

├── accounts/               # Authentication & user management

│   ├── models.py           # UserProfile with Admin/Guest roles

│   ├── forms.py            # Secure forms with whitelist validation

│   ├── views.py            # Login, register, logout, profile

│   ├── signals.py          # Auto-create profile on user creation

│   └── urls.py

├── rooms/                  # Core hotel booking CRUD

│   ├── models.py           # Room + Reservation models (UUID pk)

│   ├── forms.py            # Booking forms with date/capacity validation

│   ├── views.py            # RBAC + IDOR protected views

│   └── urls.py

├── audit/                  # Security audit trail

│   ├── models.py           # AuditLog model

│   └── views.py            # Admin-only log viewer

├── hotelbook/              # Project configuration

│   ├── settings.py         # OWASP-hardened Django settings

│   ├── middleware.py       # SecurityHeadersMiddleware + AuditMiddleware

│   ├── error_views.py      # Custom error handlers

│   └── urls.py

├── templates/              # HTML templates (luxury dark gold theme)

│   ├── base.html           # Master layout with sidebar

│   ├── accounts/           # Login, register, profile, locked

│   ├── rooms/              # Dashboard, room list, booking pages

│   ├── audit/              # Security audit log page

│   └── errors/             # 400, 403, 404, 500 error pages

├── .env.example            # Environment variables template (no real secrets)

├── .gitignore              # Excludes .env, db.sqlite3, logs

├── manage.py               # Django management tool

├── requirements.txt        # Python dependencies

└── setup_demo.py           # Demo accounts and room data setup

---

## 🧪 Security Testing Summary

| Tool | Type | Before Hardening | After Hardening |
|------|------|-----------------|-----------------|
| Bandit | Static Analysis (SAST) | 10+ issues found | 0 issues |
| Snyk | SCA / Dependency Scan | Multiple CVEs | 0 vulnerabilities |
| OWASP ZAP | Dynamic Testing | Multiple alerts | 0 High severity |
| Manual | Penetration Testing | Attacks possible | All attacks blocked |

---

## 🛡️ Vulnerabilities Found & Fixed

| Vulnerability | Attack Type | Before | After |
|--------------|-------------|--------|-------|
| SQL Injection | A03 | Raw SQL queries | Django ORM only |
| CSRF Attack | A05 | CSRF disabled | CsrfViewMiddleware enabled |
| Brute Force | A07 | Unlimited attempts | Locked after 5 attempts |
| IDOR | A01 | No ownership check | guest=request.user filter |
| Weak Hashing | A02 | MD5 password hash | bcrypt hashing |
| XSS | A03 | No output encoding | Template auto-escaping |
| Missing Headers | A05 | No security headers | CSP, X-Frame, X-Content |
| Weak Session | A07 | No timeout, no HttpOnly | 30min timeout, HttpOnly |

---

## 📊 Manual Code Review Checklist

| No | Item | Status | Evidence |
|----|------|--------|---------|
| 1 | Input Validation | ✅ Pass | accounts/forms.py — whitelist regex |
| 2 | Authentication & Session | ✅ Pass | bcrypt, 30min timeout, HttpOnly |
| 3 | Access Control | ✅ Pass | RBAC + IDOR prevention |
| 4 | Error Handling | ✅ Pass | Custom 400/403/404/500 pages |
| 5 | Sensitive Data Protection | ✅ Pass | bcrypt, no plaintext in logs |
| 6 | File Upload Security | ✅ Pass | media_private/ outside web root |
| 7 | Configuration Security | ✅ Pass | .env file, .gitignore excludes .env |
| 8 | Logging & Monitoring | ✅ Pass | AuditLog + security.log |
| 9 | Dependency Management | ✅ Pass | Snyk scan — 0 CVEs |
| 10 | Output Encoding | ✅ Pass | Django template auto-escaping |

---

## 🔗 References

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/
- Django Security: https://docs.djangoproject.com/en/5.2/topics/security/
- SSDF (NIST): https://csrc.nist.gov/projects/ssdf
- django-axes docs: https://django-axes.readthedocs.io/
- Bandit docs: https://bandit.readthedocs.io/
- OWASP ZAP: https://www.zaproxy.org/

---

## 📄 License

This project is developed for academic purposes — UniKL MIIT IKB21503 Secure Software Development.
