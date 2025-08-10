# 📌 Job Board API

A production-ready RESTful backend built with **FastAPI** for managing job postings, applications, and role-based access for companies and applicants.

This API implements **authentication, authorization, email verification, file uploads, pagination, and search** following backend best practices.

---

## ✨ Features

- **User Authentication & Email Verification** (JWT-based auth)
- **Role-Based Access Control**
  - `applicant` – browse & apply to jobs, track applications
  - `company` – create & manage job postings, view applications
- **Job Management** (CRUD with ownership enforcement)
- **Application Management** (file upload to Cloudinary)
- **Pagination, Filtering, and Search**
- **Status Transitions & Business Rules Enforcement**
- **Automated Email Notifications**
- **Database Migrations with Alembic**
- **Swagger & Postman Documentation**

---

## 🛠 Tech Stack

| Layer        | Technology       |
|--------------|------------------|
| Framework    | FastAPI          |
| Database     | PostgreSQL       |
| ORM          | SQLAlchemy       |
| Migrations   | Alembic          |
| Auth         | JWT (PyJWT)      |
| File Upload  | Cloudinary SDK   |
| Email        | SMTP / API-based |
| Env Vars     | python-dotenv    |

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/jobboard-api.git
cd jobboard-api
```


SWAGGER LINK: https://jobboard-qnmf.onrender.com/docs

## Some API TESTS RESULTS

SIGNUP: <img width="975" height="524" alt="Screenshot from 2025-08-10 12-34-53" src="https://github.com/user-attachments/assets/d8b9b7a9-fd4b-47ee-b1f6-179a17fe69ed" />
VERIFY MAIL: <img width="975" height="524" alt="Screenshot from 2025-08-10 12-40-24" src="https://github.com/user-attachments/assets/46ae924a-0bf2-410e-9a49-056b86af86fb" />
LOGIN (Valid Credentials): <img width="975" height="524" alt="image" src="https://github.com/user-attachments/assets/f38850e5-42e2-4a49-b3b2-0d637dfec0a9" />

 
