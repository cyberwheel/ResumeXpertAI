// frontend/static/app.js

// ---------- Utility: API helper ----------
const api = async (path, opts = {}) => {
  const url = path.startsWith("/") ? path : `/${path}`;
  const res = await fetch(url, opts);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `API error ${res.status}`);
  }
  return res.headers.get("content-type")?.includes("application/json")
    ? res.json()
    : res.text();
};
// ---------- GLOBAL LOADING OVERLAY ----------
function showLoader(msg = "🤖 Please wait...") {
  let overlay = document.getElementById("aiOverlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "aiOverlay";
    overlay.innerHTML = `
      <div class="ai-loader">
        <div class="spinner"></div>
        <p>${msg}</p>
      </div>
    `;
    document.body.appendChild(overlay);
  }
  overlay.querySelector("p").textContent = msg;
  overlay.classList.add("active");
  document.body.style.pointerEvents = "none";
  document.body.style.overflow = "hidden";
}

function hideLoader() {
  const overlay = document.getElementById("aiOverlay");
  if (overlay) overlay.classList.remove("active");
  document.body.style.pointerEvents = "auto";
  document.body.style.overflow = "auto";
}

// ---------- Global state ----------
let CURRENT_TEMPLATE = null;
let CURRENT_DATA = {};

// ---------- Load templates (index page) ----------
async function loadTemplates() {
  try {
    const templates = await api("/api/templates");
    const container = document.getElementById("templates");
    if (!container) return;

    container.innerHTML = "";
    templates.forEach((tpl) => {
      const div = document.createElement("div");
      div.className = "template-card";
      div.innerHTML = `
        <h3>${tpl.name}</h3>
        <p>${tpl.description}</p>
        <button class="selectTemplate" data-id="${tpl.id}">Use Template</button>
      `;
      container.appendChild(div);
    });

    document.querySelectorAll(".selectTemplate").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        const id = e.target.getAttribute("data-id");
        window.location.href = `/builder.html?template_id=${id}`;
      });
    });
  } catch (err) {
    console.error("Error loading templates:", err);
    alert("Failed to load templates: " + err.message);
  }
}

// ---------- Build the Resume Form ----------
function buildForm() {
  const container = document.getElementById("formContainer");
  if (!container) return;

  container.innerHTML = `
    <form id="resumeForm">
      <h3>Personal Details</h3>
      <input id="name" placeholder="Full Name" required />
      <input id="title" placeholder="Professional Title" />
      <input id="email" placeholder="Email" required />
      <input id="phone" placeholder="Phone" required />
      <h3>Summary</h3>
      <textarea id="summary" placeholder="Professional summary"></textarea>

      <h3>🎓 Education</h3>
      <input id="edu_10_school" placeholder="Class 10 School" />
      <input id="edu_10_year" placeholder="Year" />
      <input id="edu_10_score" placeholder="Score" />
      <input id="edu_12_school" placeholder="Intermediate College" />
      <input id="edu_12_year" placeholder="Year" />
      <input id="edu_12_score" placeholder="Score" />
      <input id="edu_inst" placeholder="Degree College" />
      <input id="edu_year" placeholder="Year" />
      <input id="edu_score" placeholder="CGPA" />

      <h3>Experience</h3>
      <textarea id="experience" rows="3" placeholder="Experience details"></textarea>

      <h3>Skills</h3>
      <input id="skills" placeholder="Comma-separated skills" />
      <div class="ai-btns">
        <button type="button" id="sampleBtn">📋 Sample Data</button>
        <button type="button" id="enhanceBtn">🚀 Enhance with AI</button>
        <button type="button" id="generateBtn">✨ Generate Summary with AI</button>
      </div>
      <div class="actions">
        <button type="submit" class="cta">Preview</button>
        

        <button type="button" id="downloadBtn" class="cta secondary">Download PDF</button>
      </div>
    </form>
  `;

  // ✅ Attach listeners *after* inserting HTML
  document.getElementById("resumeForm").addEventListener("submit", previewResume);
  document.getElementById("downloadBtn").addEventListener("click", generatePDF);

  console.log("✅ Form & buttons ready");
  document.getElementById("sampleBtn").addEventListener("click", fillSampleData);
  document.getElementById("generateBtn").addEventListener("click", generateWithAI);
  document.getElementById("enhanceBtn").addEventListener("click", enhanceWithAI);
}


      
// ---------- Read Form Data ----------
function safe(id) {
  const el = document.getElementById(id);
  return el ? el.value.trim() : "";
}

function readFormData() {
  return {
    name: safe("name"),
    title: safe("title"),
    email: safe("email"),
    phone: safe("phone"),
    summary: safe("summary"),
    skills: safe("skills").split(",").map(s => s.trim()).filter(Boolean),
    experience: safe("experience").split(/\n+/).filter(Boolean),
    education: {
      class10: {
        school: safe("edu_10_school"),
        year: safe("edu_10_year"),
        score: safe("edu_10_score"),
      },
      inter: {
        school: safe("edu_12_school"),
        year: safe("edu_12_year"),
        score: safe("edu_12_score"),
      },
      degree: {
        school: safe("edu_inst"),
        year: safe("edu_year"),
        score: safe("edu_score"),
      },
    },
  };
}

// ---------- Fill Sample Data ----------
function fillSampleData() {
  const d = {
    name: "John",
    title: "Aspiring Data Scientist",
    email: "email@example.com",
    phone: "+91 9876543210",
    summary: "Driven data enthusiast with project experience in ML model development.",
    skills: "Python, Pandas, SQL, Scikit-learn, Deep Learning",
    experience: "Intern - Data Cleaning and Analysis\nML Project - Predictive Model",
  };
  Object.entries(d).forEach(([k, v]) => {
    const el = document.getElementById(k);
    if (el) el.value = v;
  });
  document.getElementById("edu_10_school").value = "School Name";
  document.getElementById("edu_10_year").value = "2022";
  document.getElementById("edu_10_score").value = "95%";
  document.getElementById("edu_12_school").value = "Junior College";
  document.getElementById("edu_12_year").value = "2024";
  document.getElementById("edu_12_score").value = "88%";
  document.getElementById("edu_inst").value = "Engineering  College";
  document.getElementById("edu_year").value = "2028";
  document.getElementById("edu_score").value = "8.6CGPA";
  previewResume(new Event('submit'));

}

// ---------- AI Generation ----------
// ---------- AI Generation ----------
async function generateWithAI() {
  const data = readFormData();
  const template_id = new URLSearchParams(window.location.search).get("template_id");

  showLoader("🤖 Generating your summary with AI...");

  try {
    const res = await api("/suggest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ template_id, data, mode: "summary" }),
    });

    // ✅ Handle different response formats safely
    const text =
      typeof res === "string"
        ? res
        : res.text || res.summary || res.message || "";

    if (text.trim()) {
      document.getElementById("summary").value = text.trim();
      previewResume(new Event("submit"));
    } else {
      alert("⚠️ AI returned an empty response.");
    }
  } catch (err) {
    console.error("AI generation failed:", err);
    alert("❌ AI generation failed. Check server logs.");
  } finally {
    hideLoader();
  }
}


async function enhanceWithAI() {
  const data = readFormData();
  const template_id = new URLSearchParams(window.location.search).get("template_id");

  showLoader("🚀 Enhancing your summary with AI...");

  try {
    const res = await api("/suggest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ template_id, data, mode: "enhance" }),
    });

    const text =
      typeof res === "string"
        ? res
        : res.text || res.summary || res.message || "";

    if (text.trim()) {
      document.getElementById("summary").value = text.trim();
      previewResume(new Event("submit"));
    } else {
      alert("⚠️ AI returned an empty response.");
    }
  } catch (err) {
    console.error("AI enhancement failed:", err);
    alert("❌ AI enhancement failed. Check server logs.");
  } finally {
    hideLoader();
  }
}


// ---------- GLOBAL LOADING OVERLAY ----------
function showLoader(msg = "🤖 Generating with AI... Please wait") {
  let overlay = document.getElementById("aiOverlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.id = "aiOverlay";
    overlay.innerHTML = `
      <div class="ai-loader">
        <div class="spinner"></div>
        <p>${msg}</p>
      </div>
    `;
    document.body.appendChild(overlay);
  }
  overlay.querySelector("p").textContent = msg;
  overlay.style.display = "flex";
  document.body.style.pointerEvents = "none";
  document.body.style.overflow = "hidden";
}

function hideLoader() {
  const overlay = document.getElementById("aiOverlay");
  if (overlay) overlay.style.display = "none";
  document.body.style.pointerEvents = "auto";
  document.body.style.overflow = "auto";
}


// ---------- Preview ----------
async function previewResume(e) {
  e.preventDefault();
  const template_id = new URLSearchParams(window.location.search).get("template_id");
  const data = readFormData();
  CURRENT_DATA = data;

  const fd = new FormData();
  fd.append("template_id", template_id);
  fd.append("data_json", JSON.stringify(data));

  const res = await fetch("/preview", { method: "POST", body: fd });
  const html = await res.text();
  const frame = document.getElementById("previewFrame");
  const doc = frame.contentDocument || frame.contentWindow.document;
  doc.open();
  doc.write(html);
  doc.close();
}

// ---------- Generate PDF (Direct Download) ----------
async function generatePDF() {
  console.log("📄 Download button clicked");

  const template_id = new URLSearchParams(window.location.search).get("template_id");
  const data = readFormData();

  showLoader("📄 Generating your PDF...");

  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ template_id, formData: data }),
    });

    if (!response.ok) {
      const txt = await response.text();
      throw new Error(`Server error ${response.status}: ${txt}`);
    }

    const blob = await response.blob();
    if (!blob || blob.size === 0) throw new Error("Empty PDF blob received.");

    // ✅ Force browser download
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Resume_${template_id}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);

    console.log("✅ PDF downloaded successfully");
  } catch (err) {
    console.error("❌ PDF generation error:", err);
    alert("PDF generation failed: " + err.message);
  } finally {
    hideLoader();
  }
}




// ---------- Initialize ----------
document.addEventListener("DOMContentLoaded", async () => {
  const isIndex = document.getElementById("templates");
  const isBuilder = document.getElementById("formContainer");

  if (isIndex) await loadTemplates();
  if (isBuilder) {
    buildForm();
    const id = new URLSearchParams(window.location.search).get("template_id");
    if (id) CURRENT_TEMPLATE = { id };
  }
});
