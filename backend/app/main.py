import os
import json
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from jinja2 import Template as JinjaTemplate
from sqlalchemy import select
from weasyprint import HTML, CSS

# ---------------- LOCAL IMPORTS ----------------
from backend.app import schemas
from backend.app import llm
from backend.app.db import async_session_maker
from backend.app.models import Template as TemplateModel
from backend.app.llm import call_openai

# ---------------- PATH CONFIG ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
PDF_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "generated_pdfs"))
UPLOAD_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "uploads"))

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "resumexpert.db"))

print(f"✅ Starting ResumeXpert backend\nDB: {DB_PATH}\nFrontend: {FRONTEND_DIR}")

# ---------------- APP SETUP ----------------
app = FastAPI(title="ResumeXpert Backend")

# Allow frontend calls locally and on server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    print("⚠️  Warning: Static directory not found:", STATIC_DIR)


# ---------------- UTILS ----------------
async def fetch_templates_async():
    async with async_session_maker() as session:
        result = await session.execute(select(TemplateModel))
        return result.scalars().all()


def render_html_from_template(html_tpl: str, css: str, data: dict) -> str:
    """Render Jinja template and embed CSS inline."""
    rendered = JinjaTemplate(html_tpl).render(**(data or {}))
    return f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width,initial-scale=1"/>
        <style>{css or ''}</style>
      </head>
      <body>{rendered}</body>
    </html>
    """


# ---------------- ROUTES ----------------
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(path):
        return HTMLResponse("<h1>ResumeXpert backend running</h1>")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.get("/builder.html", response_class=HTMLResponse)
async def serve_builder():
    path = os.path.join(FRONTEND_DIR, "builder.html")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="builder.html not found")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


# ---------------- TEMPLATE ROUTES ----------------
@app.get("/api/templates")
async def list_templates():
    templates = await fetch_templates_async()
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "requires_photo": bool(getattr(t, "requires_photo", 0)),
        }
        for t in templates
    ]


@app.get("/api/templates/{tid}")
async def get_template(tid: int):
    async with async_session_maker() as session:
        result = await session.execute(select(TemplateModel).where(TemplateModel.id == tid))
        tpl = result.scalar_one_or_none()

    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")

    return {
        "id": tpl.id,
        "name": tpl.name,
        "description": tpl.description,
        "html": tpl.html,
        "css": tpl.css,
    }


# ---------------- PREVIEW ----------------
@app.post("/preview", response_class=HTMLResponse)
async def preview(template_id: int = Form(...), data_json: str = Form(...)):
    try:
        data = json.loads(data_json or "{}")
    except Exception:
        data = {}

    async with async_session_maker() as session:
        result = await session.execute(select(TemplateModel).where(TemplateModel.id == template_id))
        tpl = result.scalar_one_or_none()

    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")

    html = render_html_from_template(tpl.html, tpl.css, data)
    return HTMLResponse(content=html)


# ---------------- GENERATE PDF ----------------
@app.post("/generate")
async def generate_resume(data: dict = Body(...)):
    """
    Expects JSON { "template_id": <id>, "formData": { ... } }
    Returns generated PDF as a FileResponse.
    """
    template_id = data.get("template_id")
    user_data = data.get("formData", {})

    if not template_id:
        raise HTTPException(status_code=400, detail="Missing template_id")

    async with async_session_maker() as session:
        result = await session.execute(select(TemplateModel).where(TemplateModel.id == int(template_id)))
        tpl = result.scalar_one_or_none()

    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")

    # ✅ Predefine PDF path early
    filename = f"resume_{template_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = os.path.join(PDF_DIR, filename)
    os.makedirs(PDF_DIR, exist_ok=True)

    try:
        # Render HTML
        full_html = render_html_from_template(tpl.html, tpl.css or "", user_data)

        # Generate PDF safely
        HTML(string=full_html).write_pdf(pdf_path, stylesheets=[CSS(string=tpl.css or "")])

        if not os.path.exists(pdf_path):
            raise Exception("PDF file not created")

        print(f"✅ PDF successfully generated at {pdf_path}")
        return FileResponse(pdf_path, filename=filename, media_type="application/pdf")

    except Exception as e:
        print("❌ PDF generation failed:", str(e))
        # Optional: Write failing HTML for debug
        debug_path = os.path.join(PDF_DIR, f"failed_{template_id}.html")
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(full_html if 'full_html' in locals() else "No HTML rendered.")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")



# ---------------- DOWNLOAD ----------------
@app.get("/download/{filename}")
async def download(filename: str):
    fpath = os.path.join(PDF_DIR, filename)
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=fpath, filename=filename, media_type="application/pdf")


# ---------------- AI GENERATION ----------------
@app.post("/suggest")
async def suggest(inp: dict = Body(...)):
    try:
        template_id = inp.get("template_id")
        mode = inp.get("mode", "summary")
        data = inp.get("data", {})

        # You can safely ignore template_id if not needed
        prompt = ""
        if mode == "summary":
            prompt = (
                f"Write a concise 3-line professional resume summary based on this info:\n{data}"
            )
        elif mode == "enhance":
            prompt = (
                f"Enhance this resume summary to sound formal, polished, and recruiter-friendly:\n{data.get('summary', '')}"
            )
        else:
            prompt = (
                f"Provide feedback to make this resume more clear and ATS-friendly:\n{data}"
            )

        ai_resp = await call_openai(prompt)
        return {"text": ai_resp.get("text", "AI service unavailable.")}

    except Exception as e:
        print("❌ AI generation failed:", e)
        return {"text": ""}



# ---------------- ADMIN UPLOAD ----------------
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "resumeadmin")


@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    html = """
    <html><head><title>Admin - Upload Template</title></head><body>
    <h2>Admin — Upload New Template</h2>
    <form enctype='multipart/form-data' method='post' action='/admin/upload'>
      <input type='password' name='password' placeholder='Admin Password' required><br><br>
      <input type='text' name='name' placeholder='Template Name' required><br><br>
      <input type='text' name='description' placeholder='Description'><br><br>
      HTML File: <input type='file' name='html_file' accept='.html' required><br><br>
      CSS File: <input type='file' name='css_file' accept='.css'><br><br>
      <button type='submit'>Upload Template</button>
    </form>
    </body></html>
    """
    return HTMLResponse(html)


@app.post("/admin/upload")
async def admin_upload(
    password: str = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    html_file: UploadFile = File(...),
    css_file: Optional[UploadFile] = File(None),
):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid password")

    html_text = (await html_file.read()).decode("utf-8", errors="ignore")
    css_text = (await css_file.read()).decode("utf-8", errors="ignore") if css_file else ""

    async with async_session_maker() as session:
        tpl = TemplateModel(name=name, description=description, html=html_text, css=css_text, requires_photo=0)
        session.add(tpl)
        await session.commit()

    success_html = f"""
    <html><body>
      <h2>✅ Template '{name}' uploaded successfully!</h2>
      <a href='/admin'>⬅ Back to Admin</a>
    </body></html>
    """
    return HTMLResponse(success_html)


# ---------------- HEALTH CHECK ----------------
@app.get("/health")
async def health():
    return {"status": "ok", "db": DB_PATH, "frontend": FRONTEND_DIR}
