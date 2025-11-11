# backend/app/init_db.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import Base, Template as TemplateModel

# ---- Paths & DB setup ----
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "resumexpert.db"))
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Clear existing templates
db.query(TemplateModel).delete()

# ---------------------------------------
# Template blocks (Jinja2)
# ---------------------------------------

# 🟢 CLASSIC TEMPLATE
classic_html = """
<div class="header">
  <h1>{{ name }}</h1>
  {% if title %}<p><em>{{ title }}</em></p>{% endif %}
  <p>{{ email }} | {{ phone }}</p>
</div>

{% if summary %}
<div class="section">
  <h2>Profile Summary</h2>
  <p>{{ summary }}</p>
</div>
{% endif %}

{% if education.class10.school or education.inter.school or education.degree.school %}
<div class="section">
  <h2>Education</h2>
  <ul>
    {% if education.class10.school %}
      <li><strong>Class 10:</strong> {{ education.class10.school }} ({{ education.class10.year }}) — {{ education.class10.score }}</li>
    {% endif %}
    {% if education.inter.school %}
      <li><strong>Intermediate:</strong> {{ education.inter.school }} ({{ education.inter.year }}) — {{ education.inter.score }}</li>
    {% endif %}
    {% if education.degree.school %}
      <li><strong>Degree:</strong> {{ education.degree.school }} ({{ education.degree.year }}) — {{ education.degree.score }}</li>
    {% endif %}
  </ul>
</div>
{% endif %}

{% if experience and experience | select('string') | list | length > 0 %}
<div class="section">
  <h2>Experience</h2>
  <ul>
  {% for exp in experience if exp %}
    <li>{{ exp }}</li>
  {% endfor %}
  </ul>
</div>
{% endif %}

{% if skills and skills | length > 0 %}
<div class="section">
  <h2>Skills</h2>
  <p>{{ skills | join(', ') }}</p>
</div>
{% endif %}
"""

classic_css = """
body { font-family: 'Inter', sans-serif; margin: 40px; color: #222; }
h1 { font-size: 28px; margin-bottom: 2px; }
h2 { border-bottom: 2px solid #333; padding-bottom: 4px; font-size: 18px; }
.section { margin-top: 15px; }
ul { padding-left: 20px; margin-top: 6px; }
li { margin-bottom: 4px; line-height: 1.4; }
p { margin-top: 6px; line-height: 1.5; }
"""

# 🔵 MODERN TEMPLATE
modern_html = """
<header>
  <h1>{{ name }}</h1>
  {% if title %}<h3>{{ title }}</h3>{% endif %}
  <p>{{ email }} | {{ phone }}</p>
</header>

{% if summary %}
<section><h2>Summary</h2><p>{{ summary }}</p></section>
{% endif %}

{% if education.class10.school or education.inter.school or education.degree.school %}
<section><h2>Education</h2>
  {% if education.class10.school %}
    <p><strong>Class 10:</strong> {{ education.class10.school }} — {{ education.class10.score }} ({{ education.class10.year }})</p>
  {% endif %}
  {% if education.inter.school %}
    <p><strong>Intermediate:</strong> {{ education.inter.school }} — {{ education.inter.score }} ({{ education.inter.year }})</p>
  {% endif %}
  {% if education.degree.school %}
    <p><strong>Degree:</strong> {{ education.degree.school }} — {{ education.degree.score }} ({{ education.degree.year }})</p>
  {% endif %}
</section>
{% endif %}

{% if experience and experience | select('string') | list | length > 0 %}
<section><h2>Experience</h2>
  {% for exp in experience if exp %}
  <p>• {{ exp }}</p>
  {% endfor %}
</section>
{% endif %}

{% if skills and skills | length > 0 %}
<section><h2>Skills</h2><p>{{ skills | join(' • ') }}</p></section>
{% endif %}
"""

modern_css = """
body { font-family: 'Poppins', sans-serif; padding: 40px; color: #111; background: #fff; }
header { text-align: center; margin-bottom: 20px; }
h1 { margin: 0; font-size: 30px; color: #005f9e; }
h2 { margin-top: 20px; border-bottom: 1px solid #ccc; }
p { font-size: 14px; line-height: 1.5; }
"""

# 🟣 CREATIVE TEMPLATE
creative_html = """
<div class="creative-header">
  <h1>{{ name }}</h1>
  {% if title %}<p>{{ title }}</p>{% endif %}
</div>

<div class="creative-body">
  {% if summary %}
  <section><h2>About</h2><p>{{ summary }}</p></section>
  {% endif %}

  {% if education.class10.school or education.inter.school or education.degree.school %}
  <section><h2>Education</h2>
    {% if education.class10.school %}
      <p>🎓 Class 10: {{ education.class10.school }} — {{ education.class10.score }}</p>
    {% endif %}
    {% if education.inter.school %}
      <p>📘 Intermediate: {{ education.inter.school }} — {{ education.inter.score }}</p>
    {% endif %}
    {% if education.degree.school %}
      <p>🏫 Degree: {{ education.degree.school }} — {{ education.degree.score }}</p>
    {% endif %}
  </section>
  {% endif %}

  {% if experience and experience | select('string') | list | length > 0 %}
  <section><h2>Experience</h2>
    {% for exp in experience if exp %}
      <p>💼 {{ exp }}</p>
    {% endfor %}
  </section>
  {% endif %}

  {% if skills and skills | length > 0 %}
  <section><h2>Skills</h2><p>{{ skills | join(' | ') }}</p></section>
  {% endif %}
</div>
"""

creative_css = """
body { font-family: 'Inter', sans-serif; margin: 0; background: #fffefb; color: #222; }
.creative-header { background: #ffb703; padding: 25px; color: #111; }
.creative-body { padding: 25px; }
h2 { color: #444; border-bottom: 1px solid #ccc; margin-top: 15px; }
p { margin: 6px 0; line-height: 1.4; }
"""

# 🔹 ELEGANT BLUE TEMPLATE
elegant_html = """
<div class="resume-container">
  <!-- Left Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-inner">

      {% if name %}
      <section class="name-block">
        <h1>{{ name }}</h1>
        {% if title %}<h3>{{ title }}</h3>{% endif %}
      </section>
      {% endif %}

      {% if email or phone %}
      <section>
        <h2>Contact</h2>
        {% if email %}<p> {{ email }}</p>{% endif %}
        {% if phone %}<p> {{ phone }}</p>{% endif %}
      </section>
      {% endif %}

      {% if skills %}
      <section>
        <h2>Skills</h2>
        <ul>
          {% for s in skills %}
          <li>{{ s }}</li>
          {% endfor %}
        </ul>
      </section>
      {% endif %}

      

    </div>
  </aside>

  <!-- Right Content -->
  <main class="main-content">
    {% if summary %}
    <section>
      <h2>Professional Summary</h2>
      <p>{{ summary }}</p>
    </section>
    {% endif %}

    {% if experience %}
    <section>
      <h2>Experience</h2>
      <ul>
        {% for e in experience %}
        <li>{{ e }}</li>
        {% endfor %}
      </ul>
    </section>
    {% endif %}
    {% if education.class10.school or education.inter.school or education.degree.school %}
      <section>
        <h2>Education</h2>

        {% if education.class10.school %}
        <p><b>Class 10:</b> {{ education.class10.school }}
          {% if education.class10.year %} ({{ education.class10.year }}){% endif %}
          {% if education.class10.score %} — {{ education.class10.score }}{% endif %}
        </p>
        {% endif %}

        {% if education.inter.school %}
        <p><b>Intermediate:</b> {{ education.inter.school }}
          {% if education.inter.year %} ({{ education.inter.year }}){% endif %}
          {% if education.inter.score %} — {{ education.inter.score }}{% endif %}
        </p>
        {% endif %}

        {% if education.degree.school %}
        <p><b>Degree:</b> {{ education.degree.school }}
          {% if education.degree.year %} ({{ education.degree.year }}){% endif %}
          {% if education.degree.score %} — {{ education.degree.score }}{% endif %}
        </p>
        {% endif %}
      </section>
      {% endif %}
  </main>
</div>

"""

elegant_css = """
/* ================================
   💙 Elegant Blue Resume Theme (Balanced)
   ================================ */
body {
  margin: 0;
  padding: 0;
  font-family: "Poppins", "Segoe UI", sans-serif;
  color: #111;
}

.resume-container {
  display: flex;
  min-height: 100vh;
  width: 100%;
}

/* Sidebar (Left) */
.sidebar {
  width: 32%;
  background: linear-gradient(180deg, #003366 0%, #001a33 100%);
  color: white;
  padding: 40px 25px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
}

.sidebar-inner {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-evenly;
  gap: 35px;
}

.sidebar section {
  margin: 0;
}

.sidebar h1 {
  font-size: 1.8rem;
  margin: 0;
  color: #fff;
  font-weight: 700;
}

.sidebar h3 {
  font-size: 1rem;
  font-weight: 400;
  color: #b0d4ff;
  margin-top: 5px;
}

.sidebar h2 {
  font-size: 1.1rem;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 1px;
  margin-bottom: 8px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.3);
  padding-bottom: 4px;
}

.sidebar p,
.sidebar li {
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 4px 0;
}

.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

/* Main Content (Right) */
.main-content {
  width: 68%;
  padding: 45px 40px;
  background: #fdfdfd;
  color: #222;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  gap: 25px;
}

.main-content h2 {
  color: #00509e;
  font-size: 1.2rem;
  margin-bottom: 8px;
  border-bottom: 2px solid #00509e33;
  padding-bottom: 4px;
  text-transform: uppercase;
}

.main-content p {
  font-size: 0.95rem;
  line-height: 1.6;
  margin: 0;
}

.main-content ul {
  padding-left: 18px;
  margin: 0;
}

.main-content li {
  margin-bottom: 6px;
  line-height: 1.5;
}

@media print {
  .resume-container {
    min-height: auto;
  }
}

"""

# ---------------------------------------
# Store all templates in DB
# ---------------------------------------
templates = [
    ("Classic", "Traditional, clean layout", classic_html, classic_css),
    ("Modern", "Simple and balanced", modern_html, modern_css),
    ("Creative", "Vibrant and personal", creative_html, creative_css),
    ("Elegant Blue", "Sidebar professional style", elegant_html, elegant_css),
]

for name, desc, html, css in templates:
    db.add(TemplateModel(name=name, description=desc, html=html, css=css))

db.commit()
db.close()

print("✅ Templates reloaded successfully with full conditional logic.")
