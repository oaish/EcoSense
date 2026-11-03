#### 1. Start Backend:
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


#### 2. Start Frontend:
```bash
cd frontend
npm run dev
```
The frontend will be live at [`http://localhost:5173`](http://localhost:5173).
