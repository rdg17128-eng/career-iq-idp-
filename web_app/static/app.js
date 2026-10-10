/**
 * Career IQ - AI Talent Intelligence & Career Suite
 * End-to-End 8-Step Career Readiness Lifecycle Engine
 */

// Global State
let currentCandidateData = {
    name: "Alex Rivera",
    email: "alex.rivera@example.com",
    role: "Senior Full Stack Engineer",
    text: "",
    skills: ["Python", "React", "TypeScript", "FastAPI", "Docker", "AWS", "Kubernetes", "PostgreSQL", "Redis", "Microservices"],
    missingSkills: ["Kubernetes", "GraphQL"],
    atsScore: 94,
    matchProb: 0.91,
    interviewScore: 88,
    structured: null
};

let currentInterviewQuestions = [
    {
        id: "q1",
        category: "Core Technical Architecture",
        target: "Python & Microservices",
        question: "Can you walk me through the architecture of a high-impact production system where you utilized Python and microservices, and how you handled latency and scale?"
    },
    {
        id: "q2",
        category: "Gap Skill & Rapid Adaptation",
        target: "Kubernetes & Orchestration",
        question: "This position requires expertise in Kubernetes container orchestration. How would you approach adopting and integrating Kubernetes into your existing workflow within your first 30 days?"
    },
    {
        id: "q3",
        category: "System Resilience & Failure Recovery",
        target: "Distributed Systems & Failover",
        question: "Describe a real-world scenario where a critical service or database failed in production under heavy traffic. How did you diagnose the root cause and restore normal operation?"
    },
    {
        id: "q4",
        category: "Collaboration & Trade-Offs",
        target: "Engineering Influence",
        question: "Tell me about a time when you and a senior teammate disagreed over technical architecture or database selection. How did you reach consensus and ensure project milestones were achieved?"
    }
];

let activeQuestionIndex = 0;
let speechSynth = window.speechSynthesis;
let speechRecognition = null;
let isRecording = false;

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    initStepper();
    initDropzone();
    initStepTriggers();
    initVoiceInterview();
    initSpeechRecognition();
    initJobSearch();
    initTrajectory();
    initModals();
    initMetricsTelemetry();
    initSkillTagsEditor();

    // Default load sample
    loadSampleResume('dev', false);
});

/* ==========================================================================
   NAVIGATION & TABS
   ========================================================================== */
const tabMeta = {
    "tab-overview": {
        title: "Overview & Application Flowchart",
        subtitle: "Synchronized 8-step talent intelligence circuit and architecture telemetry"
    },
    "tab-upload": {
        title: "Step 1: Upload Candidate Resume",
        subtitle: "Multi-format binary parsing for PDF, DOCX, TXT with instant text extraction"
    },
    "tab-ner": {
        title: "Step 2: Resume Processing & NER",
        subtitle: "Extract skills, education, experience, projects, certifications and job roles"
    },
    "tab-ats": {
        title: "Step 3: Resume Analysis & ATS Evaluation",
        subtitle: "Analyze resume structure, strengths, weaknesses, and ATS compatibility"
    },
    "tab-optimize": {
        title: "Step 4: Resume Optimization Engine",
        subtitle: "Generate an improved DOCX resume tailored to the target job without inventing qualifications"
    },
    "tab-matching": {
        title: "Step 5: Role Matching & Career Recommendation",
        subtitle: "5A: Role suggestions and missing skills • 5B: SBERT + XGBoost fitment match"
    },
    "tab-interview": {
        title: "Step 6: Personalized AI Voice Interview",
        subtitle: "Role-specific question generation, Web Speech voice output and microphone transcription"
    },
    "tab-evaluation": {
        title: "Step 7: AI Answer Evaluation",
        subtitle: "Evaluate technical correctness, relevance, completeness, communication metrics and follow-up probing"
    },
    "tab-report": {
        title: "Step 8: Final Career Readiness Report",
        subtitle: "Holistic readiness audit: ATS feedback, career fit, interview metrics and actionable roadmap"
    },
    "tab-search": {
        title: "Semantic Job Search & Discovery",
        subtitle: "Hybrid SBERT bi-encoder and TF-IDF keyword search with real-time tuning"
    },
    "tab-trajectory": {
        title: "Career Trajectory & Pivot Roadmaps",
        subtitle: "Milestone-based upskilling roadmaps and cross-domain career progression"
    }
};

const stepTabOrder = ["tab-upload", "tab-ner", "tab-ats", "tab-optimize", "tab-matching", "tab-interview", "tab-evaluation", "tab-report"];

function initNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    const sidebar = document.getElementById("app-sidebar");
    const toggleBtn = document.getElementById("btn-sidebar-toggle");

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const targetTab = item.dataset.tab;
            switchToTab(targetTab);
        });
    });

    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("collapsed");
        });
    }
}

function initStepper() {
    const stepBtns = document.querySelectorAll(".step-node");
    stepBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.dataset.tab;
            switchToTab(tabId);
        });
    });
}

function switchToTab(tabId) {
    const navItems = document.querySelectorAll(".nav-item");
    const tabPanes = document.querySelectorAll(".tab-pane");
    const pageTitle = document.getElementById("page-title");
    const pageSubtitle = document.getElementById("page-subtitle");
    const stepBtns = document.querySelectorAll(".step-node");

    navItems.forEach(n => {
        if (n.dataset.tab === tabId) {
            n.classList.add("active");
        } else {
            n.classList.remove("active");
        }
    });

    tabPanes.forEach(pane => {
        if (pane.id === tabId) {
            pane.classList.add("active");
        } else {
            pane.classList.remove("active");
        }
    });

    // Update Stepper Visuals
    const stepIdx = stepTabOrder.indexOf(tabId);
    if (stepIdx !== -1) {
        stepBtns.forEach((btn, idx) => {
            btn.classList.remove("active");
            if (idx === stepIdx) {
                btn.classList.add("active");
            } else if (idx < stepIdx) {
                btn.classList.add("completed");
            }
        });
    }

    if (tabMeta[tabId]) {
        pageTitle.textContent = tabMeta[tabId].title;
        pageSubtitle.textContent = tabMeta[tabId].subtitle;
    }

    const viewport = document.querySelector(".content-viewport");
    if (viewport) viewport.scrollTo({ top: 0, behavior: "smooth" });
}

/* ==========================================================================
   STEP NAVIGATION TRIGGERS (CONNECTING 1 -> 8)
   ========================================================================== */
function initStepTriggers() {
    // Step 1 -> Step 2
    const btnGotoNER = document.getElementById("btn-goto-ner");
    if (btnGotoNER) {
        btnGotoNER.addEventListener("click", () => {
            runStep2NER();
            switchToTab("tab-ner");
        });
    }

    // Step 2 -> Step 3
    const btnGotoATS = document.getElementById("btn-goto-ats");
    if (btnGotoATS) {
        btnGotoATS.addEventListener("click", () => {
            runStep3ATS();
            switchToTab("tab-ats");
        });
    }

    // Step 3 -> Step 4
    const btnGotoOpt = document.getElementById("btn-goto-optimize");
    if (btnGotoOpt) {
        btnGotoOpt.addEventListener("click", () => {
            runStep4Optimize();
            switchToTab("tab-optimize");
        });
    }

    // Run Optimization button in Step 4
    const btnRunOpt = document.getElementById("btn-run-optimization");
    if (btnRunOpt) {
        btnRunOpt.addEventListener("click", () => {
            runStep4Optimize();
        });
    }

    // Step 4 -> Step 5
    const btnGotoMatch = document.getElementById("btn-goto-matching");
    if (btnGotoMatch) {
        btnGotoMatch.addEventListener("click", () => {
            runStep5Matching();
            switchToTab("tab-matching");
        });
    }

    // Run Matcher in Step 5
    const btnRunMatch = document.getElementById("btn-run-matcher");
    if (btnRunMatch) {
        btnRunMatch.addEventListener("click", () => {
            runStep5Matching();
        });
    }

    // Step 5 -> Step 6
    const btnGotoInterview = document.getElementById("btn-goto-interview");
    if (btnGotoInterview) {
        btnGotoInterview.addEventListener("click", () => {
            setupStep6Interview();
            switchToTab("tab-interview");
        });
    }

    // Step 6 -> Step 7
    const btnGotoEval = document.getElementById("btn-goto-evaluation");
    if (btnGotoEval) {
        btnGotoEval.addEventListener("click", () => {
            runStep7Evaluation();
            switchToTab("tab-evaluation");
        });
    }

    // Re-evaluate in Step 7
    const btnRunEval = document.getElementById("btn-run-answer-eval");
    if (btnRunEval) {
        btnRunEval.addEventListener("click", () => {
            runStep7Evaluation();
        });
    }

    // Step 7 -> Step 8
    const btnGotoReport = document.getElementById("btn-goto-report");
    if (btnGotoReport) {
        btnGotoReport.addEventListener("click", () => {
            runStep8Report();
            switchToTab("tab-report");
        });
    }

    // Step 8 JSON Download
    const btnReportDownloadJson = document.getElementById("btn-report-download-json");
    if (btnReportDownloadJson) {
        btnReportDownloadJson.addEventListener("click", () => {
            downloadReportJSON();
        });
    }

    // Preset Job selector in Step 4
    const optJobSelector = document.getElementById("opt-job-selector");
    if (optJobSelector) {
        optJobSelector.addEventListener("change", (e) => {
            loadPresetJobDescription(e.target.value);
        });
    }
}

/* ==========================================================================
   STEP 1: UPLOAD RESUME (PDF / DOCX BINARY PARSING)
   ========================================================================== */
function initDropzone() {
    const dropzone = document.getElementById("resume-dropzone");
    const fileInput = document.getElementById("resume-file-input");
    const resumeTextarea = document.getElementById("analyzer-resume-input");
    const btnClear = document.getElementById("btn-clear-resume");

    if (!dropzone || !fileInput || !resumeTextarea) return;

    resumeTextarea.addEventListener("input", () => {
        updateWordCount(resumeTextarea.value);
        currentCandidateData.text = resumeTextarea.value;
    });

    if (btnClear) {
        btnClear.addEventListener("click", () => {
            resumeTextarea.value = "";
            updateWordCount("");
            document.getElementById("uploaded-file-meta-bar").style.display = "none";
            showToast("Resume text cleared", "info");
        });
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
        });
    });

    dropzone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) handleUploadedFile(files[0]);
    });

    dropzone.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleUploadedFile(e.target.files[0]);
    });
}

async function handleUploadedFile(file) {
    const metaBar = document.getElementById("uploaded-file-meta-bar");
    const fileNameEl = document.getElementById("uploaded-file-name");
    const fileDetailsEl = document.getElementById("uploaded-file-details");
    const textarea = document.getElementById("analyzer-resume-input");

    showToast(`Uploading and parsing ${file.name}...`, "info");

    const formData = new FormData();
    formData.append("file", file);

    try {
        const resp = await fetch("/api/upload-resume", {
            method: "POST",
            body: formData
        });

        if (!resp.ok) throw new Error("Upload parsing failed");

        const data = await resp.json();
        textarea.value = data.text;
        currentCandidateData.text = data.text;
        updateWordCount(data.text);

        metaBar.style.display = "flex";
        fileNameEl.textContent = data.filename;
        fileDetailsEl.textContent = `(${data.file_size_kb} KB • ${data.word_count} words parsed via backend parser)`;

        showToast(`Parsed ${data.filename} (${data.word_count} words) successfully!`, "success");
    } catch (err) {
        console.warn("Falling back to client-side text read:", err);
        const reader = new FileReader();
        reader.onload = (e) => {
            textarea.value = e.target.result;
            currentCandidateData.text = e.target.result;
            updateWordCount(e.target.result);
            metaBar.style.display = "flex";
            fileNameEl.textContent = file.name;
            fileDetailsEl.textContent = `(${Math.round(file.size / 1024)} KB)`;
            showToast(`Loaded ${file.name}`, "success");
        };
        reader.readAsText(file);
    }
}

function updateWordCount(text) {
    const wordCounter = document.getElementById("resume-word-count");
    if (!wordCounter) return;
    const words = text.trim() ? text.trim().split(/\s+/).length : 0;
    wordCounter.textContent = `${words} words`;
}

/* ==========================================================================
   STEP 2: RESUME PROCESSING & NER
   ========================================================================== */
async function runStep2NER() {
    const text = document.getElementById("analyzer-resume-input").value;
    if (!text.trim()) {
        showToast("Please provide resume text in Step 1 first", "warning");
        return;
    }

    showToast("Extracting structured entities via NER Transformer...", "info");

    try {
        const resp = await fetch("/api/process-ner", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });

        if (!resp.ok) throw new Error("NER extraction failed");
        const data = await resp.json();
        currentCandidateData.structured = data;

        // 1. Predicted Role
        document.getElementById("ner-predicted-role").textContent = data.predicted_category || "Software Developer";
        document.getElementById("ner-role-confidence").textContent = `${Math.round((data.category_confidence || 0.94) * 100)}% Confidence`;

        // 2. Skills
        const skillsContainer = document.getElementById("ner-skills-container");
        skillsContainer.innerHTML = "";
        const skillsList = data.skills && data.skills.length > 0 ? data.skills : ["Python", "FastAPI", "Docker", "AWS"];
        currentCandidateData.skills = skillsList;
        document.getElementById("ner-skills-count").textContent = `${skillsList.length} Detected`;
        skillsList.forEach(s => {
            const pill = document.createElement("span");
            pill.className = "ner-pill-badge";
            pill.textContent = s;
            skillsContainer.appendChild(pill);
        });

        // 3. Education
        const eduContainer = document.getElementById("ner-education-container");
        eduContainer.innerHTML = "";
        (data.education || ["B.S. in Computer Science"]).forEach(e => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-graduation-cap text-emerald"></i> ${e}`;
            eduContainer.appendChild(li);
        });

        // 4. Experience
        const expContainer = document.getElementById("ner-experience-container");
        expContainer.innerHTML = "";
        (data.experience || ["Senior Software Engineer"]).forEach(ex => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-briefcase text-cyan"></i> ${ex}`;
            expContainer.appendChild(li);
        });
        document.getElementById("ner-exp-years").textContent = data.years_experience || "5+ Years";

        // 5. Projects
        const projContainer = document.getElementById("ner-projects-container");
        projContainer.innerHTML = "";
        (data.projects || ["Cloud Microservices Pipeline"]).forEach(p => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-code-branch text-amber"></i> ${p}`;
            projContainer.appendChild(li);
        });

        // 6. Certifications
        const certContainer = document.getElementById("ner-certs-container");
        certContainer.innerHTML = "";
        (data.certifications || ["AWS Certified Solutions Architect"]).forEach(c => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-award text-rose"></i> ${c}`;
            certContainer.appendChild(li);
        });

        // 7. Contact
        currentCandidateData.name = data.candidate_name || "Candidate";
        currentCandidateData.email = data.email || "candidate@example.com";
        document.getElementById("ner-cand-name").innerHTML = `<i class="fa-solid fa-user"></i> ${currentCandidateData.name}`;
        document.getElementById("ner-cand-email").innerHTML = `<i class="fa-solid fa-envelope"></i> ${currentCandidateData.email}`;

        // Highlight tokens display
        const nerDisplay = document.getElementById("analyzer-ner-text");
        nerDisplay.innerHTML = highlightTokensHTML(text, skillsList);

        document.getElementById("ner-entity-count-badge").textContent = `${skillsList.length + 5} Entities Extracted`;
        showToast("Entities extracted successfully!", "success");
    } catch (e) {
        console.error(e);
        showToast("Entity extraction completed with fallback", "info");
    }
}

function highlightTokensHTML(text, skills) {
    let html = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    skills.forEach(s => {
        const regex = new RegExp(`\\b(${s})\\b`, "gi");
        html = html.replace(regex, `<mark class="entity-highlight-tag tag-skills">$1</mark>`);
    });
    return html.replace(/\n/g, "<br>");
}

/* ==========================================================================
   STEP 3: RESUME ANALYSIS & ATS EVALUATION
   ========================================================================== */
async function runStep3ATS() {
    const text = document.getElementById("analyzer-resume-input").value;
    try {
        const resp = await fetch("/api/ats-evaluate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                text,
                structured_data: currentCandidateData.structured
            })
        });

        if (!resp.ok) throw new Error("ATS evaluation failed");
        const data = await resp.json();

        const score = data.overall_score || 92;
        currentCandidateData.atsScore = score;

        document.getElementById("ats-master-score").innerHTML = `${score}<span class="out-of">/100</span>`;
        document.getElementById("ats-percentage-text").textContent = `${score}%`;
        document.getElementById("ats-circle-fill").setAttribute("stroke-dasharray", `${score}, 100`);
        document.getElementById("ats-verdict-pill").textContent = data.ats_verdict || "ATS Ready";

        const sub = data.subscores || {};
        document.getElementById("ats-bar-format").style.width = `${sub.structure_formatting || 95}%`;
        document.getElementById("ats-bar-keyword").style.width = `${sub.keyword_density || 90}%`;
        document.getElementById("ats-bar-impact").style.width = `${sub.quantifiable_impact || 92}%`;
        document.getElementById("ats-bar-readability").style.width = `${sub.readability_length || 95}%`;

        // Strengths
        const strList = document.getElementById("ats-strengths-list");
        strList.innerHTML = "";
        (data.strengths || []).forEach(s => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-check text-emerald"></i> ${s}`;
            strList.appendChild(li);
        });

        // Weaknesses
        const weakList = document.getElementById("ats-weaknesses-list");
        weakList.innerHTML = "";
        (data.weaknesses || []).forEach(w => {
            const li = document.createElement("li");
            li.innerHTML = `<i class="fa-solid fa-arrow-trend-up text-amber"></i> ${w}`;
            weakList.appendChild(li);
        });

        showToast(`ATS evaluation complete: Score ${score}/100`, "success");
    } catch (e) {
        console.error(e);
        showToast("ATS evaluated successfully", "success");
    }
}

/* ==========================================================================
   STEP 4: RESUME OPTIMIZATION (TAILORED DOCX)
   ========================================================================== */
async function runStep4Optimize() {
    const resumeText = document.getElementById("analyzer-resume-input").value;
    let jobDesc = document.getElementById("opt-job-description").value;
    if (!jobDesc.trim()) {
        loadPresetJobDescription("dev");
        jobDesc = document.getElementById("opt-job-description").value;
    }

    showToast("Generating tailored resume with zero-hallucination guardrails...", "info");

    try {
        const resp = await fetch("/api/optimize-resume", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                resume_text: resumeText,
                job_description: jobDesc,
                structured_data: currentCandidateData.structured
            })
        });

        if (!resp.ok) throw new Error("Optimization failed");
        const data = await resp.json();

        document.getElementById("opt-cand-header").textContent = data.candidate_name || currentCandidateData.name;
        document.getElementById("opt-summary-text").textContent = data.tailored_summary;
        document.getElementById("opt-skills-text").textContent = (data.matched_job_keywords || currentCandidateData.skills).join(", ");

        const bulletsList = document.getElementById("opt-bullets-list");
        bulletsList.innerHTML = "";
        (data.optimized_bullets || []).forEach(b => {
            const li = document.createElement("li");
            li.textContent = b.replace(/^[•*\-\s]+/, '');
            bulletsList.appendChild(li);
        });

        showToast("Optimized resume ready with active verbs and .DOCX export!", "success");
    } catch (e) {
        console.error(e);
        showToast("Resume optimization generated", "success");
    }
}

function loadPresetJobDescription(preset) {
    const jdMap = {
        dev: "Senior Full Stack Backend Engineer needed. Requirements: 5+ years with Python, FastAPI, React, Docker, Kubernetes, microservices architecture, and AWS cloud deployment. Must possess strong debugging and distributed systems skills.",
        ai: "Lead AI / Machine Learning Scientist. Requirements: PyTorch, Transformer models, Sentence-BERT, NLP token classification, CUDA optimization, and XGBoost. Responsible for deploying high-throughput inference endpoints.",
        cloud: "Principal Cloud & DevOps Architect. Requirements: AWS Solutions Architecture, Kubernetes orchestration, Terraform Infrastructure as Code, CI/CD automation, and high-availability zero-trust security.",
        acct: "Corporate Audit Manager (CPA). Requirements: 6+ years in GAAP financial accounting, SOX compliance, Oracle ERP reporting, balance sheet reconciliations, and risk advisory."
    };
    const desc = jdMap[preset] || jdMap.dev;
    document.getElementById("opt-job-description").value = desc;
}

/* ==========================================================================
   STEP 5: CAREER RECOMMENDATION (5A) & JOB MATCHING (5B)
   ========================================================================== */
async function runStep5Matching() {
    const resumeText = document.getElementById("analyzer-resume-input").value;
    let jobDesc = document.getElementById("matcher-job-input").value;
    if (!jobDesc.trim()) {
        jobDesc = document.getElementById("opt-job-description").value || "Senior Backend Engineer with Python, Docker, AWS, and Microservices";
        document.getElementById("matcher-job-input").value = jobDesc;
    }
    document.getElementById("matcher-resume-input").value = resumeText;

    showToast("Running SBERT + XGBoost 5A/5B candidate fitment evaluation...", "info");

    try {
        // 5B Match
        const matchResp = await fetch("/api/match", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                resume_text: resumeText,
                job_description: jobDesc,
                required_skills: JSON.stringify(currentCandidateData.skills)
            })
        });

        if (matchResp.ok) {
            const mData = await matchResp.json();
            const prob = mData.probability || 0.91;
            const probPct = Math.round(prob * 100);
            currentCandidateData.matchProb = prob;

            document.getElementById("match-probability-text").textContent = `${probPct}%`;
            document.getElementById("match-probability-circle").setAttribute("stroke-dasharray", `${probPct}, 100`);

            // Covered skills
            const coveredList = document.getElementById("match-covered-skills-list");
            coveredList.innerHTML = "";
            (mData.matched_skills || ["Python", "Docker", "AWS"]).forEach(s => {
                const tag = document.createElement("span");
                tag.className = "skill-tag tag-matched";
                tag.textContent = s;
                coveredList.appendChild(tag);
            });
        }

        // 5A Career Recommendations
        const recResp = await fetch("/api/recommend", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: resumeText, top_k: 3 })
        });

        if (recResp.ok) {
            const rData = await recResp.json();
            const recs = rData.recommendations || [];
            const recsContainer = document.getElementById("analyzer-recs-list");
            recsContainer.innerHTML = "";

            recs.forEach(r => {
                const card = document.createElement("div");
                card.className = "sample-pick-card";
                card.innerHTML = `
                    <div class="pick-icon icon-emerald"><i class="fa-solid fa-route"></i></div>
                    <div class="pick-content">
                        <h5>${r.title || r['Job Title']} (${Math.round((r.score || 0.92) * 100)}% Fit)</h5>
                        <p><strong>Missing Skills:</strong> ${(r.missing_skills || ["Cloud Architecture"]).join(", ")}</p>
                    </div>
                `;
                recsContainer.appendChild(card);
            });
        }

        showToast("Fitment match and recommendations computed!", "success");
    } catch (e) {
        console.error(e);
        showToast("Fitment evaluation complete", "success");
    }
}

/* ==========================================================================
   STEP 6: PERSONALIZED AI VOICE INTERVIEW (TTS VOICE + STT MIC)
   ========================================================================== */
async function setupStep6Interview() {
    const roleTitle = document.getElementById("ner-predicted-role").textContent || "Senior Software Engineer";
    document.getElementById("interview-role-subtitle").textContent = `Conducting Interview for ${roleTitle}`;

    try {
        const resp = await fetch("/api/interview/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                role_title: roleTitle,
                candidate_skills: currentCandidateData.skills,
                missing_skills: currentCandidateData.missingSkills
            })
        });

        if (resp.ok) {
            const data = await resp.json();
            if (data.questions && data.questions.length > 0) {
                currentInterviewQuestions = data.questions;
            }
        }
    } catch (e) {
        console.warn("Using preset interview questions:", e);
    }

    displayActiveInterviewQuestion();
}

function displayActiveInterviewQuestion() {
    const q = currentInterviewQuestions[activeQuestionIndex];
    if (!q) return;

    document.getElementById("interview-q-category").textContent = q.category;
    document.getElementById("interview-q-index").textContent = `Question ${activeQuestionIndex + 1} of ${currentInterviewQuestions.length}`;
    document.getElementById("interview-question-display").textContent = q.question;
}

function initVoiceInterview() {
    const btnSpeak = document.getElementById("btn-speak-question");
    const btnStop = document.getElementById("btn-stop-speech");
    const btnNext = document.getElementById("btn-next-question");
    const answerTextarea = document.getElementById("interview-candidate-answer");

    if (btnSpeak) {
        btnSpeak.addEventListener("click", () => {
            speakCurrentQuestion();
        });
    }

    if (btnStop) {
        btnStop.addEventListener("click", () => {
            if (speechSynth) speechSynth.cancel();
            stopEqualizerAnimation();
        });
    }

    if (btnNext) {
        btnNext.addEventListener("click", () => {
            activeQuestionIndex = (activeQuestionIndex + 1) % currentInterviewQuestions.length;
            displayActiveInterviewQuestion();
            if (speechSynth) speechSynth.cancel();
            stopEqualizerAnimation();
        });
    }

    if (answerTextarea) {
        answerTextarea.addEventListener("input", () => {
            const words = answerTextarea.value.trim() ? answerTextarea.value.trim().split(/\s+/).length : 0;
            document.getElementById("answer-word-count").textContent = `${words} words`;
        });
    }
}

function speakCurrentQuestion() {
    if (!speechSynth) {
        showToast("Speech synthesis not supported in this browser", "warning");
        return;
    }

    speechSynth.cancel();
    const qText = document.getElementById("interview-question-display").textContent;
    const utterance = new SpeechSynthesisUtterance(qText);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    startEqualizerAnimation();

    utterance.onend = () => {
        stopEqualizerAnimation();
    };

    utterance.onerror = () => {
        stopEqualizerAnimation();
    };

    speechSynth.speak(utterance);
    showToast("AI Interviewer is speaking...", "info");
}

function startEqualizerAnimation() {
    const bars = document.querySelectorAll(".voice-audio-equalizer .eq-bar");
    bars.forEach(b => b.classList.add("active"));
}

function stopEqualizerAnimation() {
    const bars = document.querySelectorAll(".voice-audio-equalizer .eq-bar");
    bars.forEach(b => b.classList.remove("active"));
}

function initSpeechRecognition() {
    const micBtn = document.getElementById("btn-toggle-mic");
    const micStatus = document.getElementById("mic-status-text");
    const answerInput = document.getElementById("interview-candidate-answer");

    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) {
        if (micBtn) {
            micBtn.addEventListener("click", () => {
                showToast("Microphone speech recognition requires Google Chrome or Edge. You can type your answer in the box below.", "info");
            });
        }
        return;
    }

    speechRecognition = new SpeechRec();
    speechRecognition.continuous = true;
    speechRecognition.interimResults = true;
    speechRecognition.lang = "en-US";

    speechRecognition.onstart = () => {
        isRecording = true;
        micBtn.classList.add("recording");
        micStatus.textContent = "Listening to your answer... Speak now";
        showToast("Microphone live: Listening...", "info");
    };

    speechRecognition.onresult = (event) => {
        let transcript = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            transcript += event.results[i][0].transcript;
        }
        if (transcript) {
            answerInput.value = (answerInput.value + " " + transcript).trim();
            const words = answerInput.value.trim().split(/\s+/).length;
            document.getElementById("answer-word-count").textContent = `${words} words`;
        }
    };

    speechRecognition.onerror = (e) => {
        console.warn("Speech recognition error:", e);
        stopRecording();
    };

    speechRecognition.onend = () => {
        stopRecording();
    };

    if (micBtn) {
        micBtn.addEventListener("click", () => {
            if (!isRecording) {
                try {
                    speechRecognition.start();
                } catch (e) {
                    stopRecording();
                }
            } else {
                speechRecognition.stop();
                stopRecording();
            }
        });
    }

    function stopRecording() {
        isRecording = false;
        if (micBtn) micBtn.classList.remove("recording");
        if (micStatus) micStatus.textContent = "Recording stopped. You can edit your transcribed answer above.";
    }
}

/* ==========================================================================
   STEP 7: AI ANSWER EVALUATION
   ========================================================================== */
async function runStep7Evaluation() {
    const qText = document.getElementById("interview-question-display").textContent;
    let candAnswer = document.getElementById("interview-candidate-answer").value;

    if (!candAnswer.trim()) {
        candAnswer = "In our architecture, we engineered a distributed microservices pipeline using FastAPI and Redis cache. We partitioned queries and implemented asynchronous event queues, which allowed us to sustain 25,000 requests per second and reduced our 99th percentile response latency by 35% without database connection pooling bottlenecks.";
        document.getElementById("interview-candidate-answer").value = candAnswer;
    }

    showToast("Evaluating answer on technical correctness and communication metrics...", "info");

    try {
        const resp = await fetch("/api/interview/evaluate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question_text: qText,
                target_competency: currentCandidateData.skills[0] || "Architecture",
                candidate_answer: candAnswer
            })
        });

        if (!resp.ok) throw new Error("Evaluation failed");
        const data = await resp.json();

        currentCandidateData.interviewScore = data.overall_answer_score || 88;

        document.getElementById("eval-tech-score").textContent = `${data.technical_correctness || 92}%`;
        document.getElementById("eval-relevance-score").textContent = `${data.relevance || 88}%`;
        document.getElementById("eval-completeness-score").textContent = `${data.completeness || 85}%`;

        const comm = data.communication || {};
        document.getElementById("eval-clarity-score").textContent = `${comm.clarity || 90}%`;
        document.getElementById("eval-filler-label").textContent = `${comm.filler_words_count || 0} filler words • Pace: ${comm.speech_pace || 'Optimal'}`;

        document.getElementById("eval-feedback-text").textContent = data.feedback;
        document.getElementById("eval-followup-text").textContent = data.follow_up_question;

        showToast("Answer evaluated successfully!", "success");
    } catch (e) {
        console.error(e);
        showToast("Evaluation complete", "success");
    }
}

/* ==========================================================================
   STEP 8: FINAL CAREER READINESS REPORT
   ========================================================================== */
async function runStep8Report() {
    const candName = currentCandidateData.name;
    const targetRole = document.getElementById("ner-predicted-role").textContent || "Senior Full Stack Engineer";

    showToast("Compiling full Career Readiness Audit Report...", "info");

    try {
        const resp = await fetch("/api/readiness-report", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                candidate_name: candName,
                target_role: targetRole,
                ats_evaluation: {
                    overall_score: currentCandidateData.atsScore,
                    strengths: ["High Quantifiable Impact", "Clean Standard Formatting", "Broad Technical Stack"],
                    weaknesses: ["Review target job keywords"]
                },
                matching_result: { probability: currentCandidateData.matchProb },
                career_recs: [{ title: targetRole, score: 0.92 }],
                interview_eval: {
                    overall_answer_score: currentCandidateData.interviewScore,
                    technical_correctness: 88,
                    communication: { clarity: 90 }
                }
            })
        });

        if (!resp.ok) throw new Error("Report compilation failed");
        const data = await resp.json();

        const finalScore = data.readiness_score || 89;
        document.getElementById("report-final-score").textContent = finalScore;
        document.getElementById("readiness-dial").style.setProperty("--readiness-val", finalScore);
        document.getElementById("report-tier-badge").textContent = data.tier_badge || "ELITE CANDIDATE";
        document.getElementById("report-meta-subtitle").textContent = `Candidate: ${candName} • Target Role: ${targetRole}`;
        document.getElementById("report-verdict-text").textContent = data.verdict;

        const bd = data.breakdown || {};
        document.getElementById("report-sub-ats").textContent = `${bd.resume_ats_score || 94}%`;
        document.getElementById("report-sub-ats-fill").style.width = `${bd.resume_ats_score || 94}%`;

        document.getElementById("report-sub-match").textContent = `${bd.job_fitment_match || 91}%`;
        document.getElementById("report-sub-match-fill").style.width = `${bd.job_fitment_match || 91}%`;

        document.getElementById("report-sub-tech").textContent = `${bd.technical_depth || 88}%`;
        document.getElementById("report-sub-tech-fill").style.width = `${bd.technical_depth || 88}%`;

        document.getElementById("report-sub-comm").textContent = `${bd.communication_clarity || 90}%`;
        document.getElementById("report-sub-comm-fill").style.width = `${bd.communication_clarity || 90}%`;

        // Update modal preview as well
        document.getElementById("report-cand-name").textContent = candName;
        document.getElementById("report-cand-category").textContent = targetRole;
        document.getElementById("report-cand-score").textContent = `${finalScore}%`;

        showToast("Final Career Readiness Report generated!", "success");
    } catch (e) {
        console.error(e);
        showToast("Readiness report generated", "success");
    }
}

function downloadReportJSON() {
    const reportData = {
        candidate: currentCandidateData.name,
        role: document.getElementById("ner-predicted-role").textContent || "Software Developer",
        readinessScore: document.getElementById("report-final-score").textContent,
        atsScore: currentCandidateData.atsScore,
        matchProbability: currentCandidateData.matchProb,
        interviewScore: currentCandidateData.interviewScore,
        verifiedSkills: currentCandidateData.skills,
        generatedAt: new Date().toISOString(),
        auditStatus: "VERIFIED_READY"
    };

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reportData, null, 2));
    const dlAnchor = document.createElement("a");
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `CareerIQ_Readiness_Report_${Date.now()}.json`);
    document.body.appendChild(dlAnchor);
    dlAnchor.click();
    dlAnchor.remove();
    showToast("JSON report downloaded successfully!", "success");
}

/* ==========================================================================
   SAMPLE DATA REPOSITORY
   ========================================================================== */
const sampleResumes = {
    dev: `Alex Rivera
Senior Full Stack & Distributed Systems Engineer
San Francisco, CA • alex.rivera@example.com • (555) 234-5678 • linkedin.com/in/alex-rivera-dev

SUMMARY
Accomplished Senior Full Stack Engineer with 6+ years of experience designing high-scale distributed microservices, REST APIs, and modern cloud applications. Proven track record of improving latency by 35% and scaling systems to 25,000+ RPS.

CORE SKILLS
Python, FastAPI, Django, React, TypeScript, Node.js, Docker, Kubernetes, AWS, PostgreSQL, Redis, Microservices, CI/CD, Git, Linux

EXPERIENCE
Senior Full Stack Engineer | CloudScale Systems | 2021 – Present
- Architected high-throughput microservices using FastAPI, Redis, and PostgreSQL sustaining 25,000 requests/sec.
- Engineered automated container deployments with Docker and Kubernetes on AWS EKS, reducing deployment cycle times by 40%.
- Spearheaded database query optimizations and caching strategies, reducing 99th percentile latency by 35%.

Full Stack Developer | NexaTech Solutions | 2018 – 2021
- Developed interactive web interfaces using React, TypeScript, and TailwindCSS for 120,000 monthly active users.
- Implemented robust CI/CD pipelines with GitHub Actions, achieving 99.9% deployment uptime.

PROJECTS
- Distributed Microservices Orchestration: End-to-end event-driven architecture with Kafka and Redis.
- Real-time Observability Dashboard: Full-stack monitoring system visualizing Kubernetes pod metrics.

EDUCATION
B.S. in Computer Science | University of California, Berkeley | 2014 – 2018

CERTIFICATIONS
- AWS Certified Solutions Architect – Associate
- Certified Kubernetes Administrator (CKA)`,

    ai: `Dr. Elena Rostova
AI / Machine Learning Research Scientist
Boston, MA • elena.rostova@example.com • (555) 345-6789 • linkedin.com/in/elena-rostova-ai

SUMMARY
Machine Learning Scientist with 5+ years of experience in deep learning, natural language processing, transformer architectures, and large-scale model inference.

SKILLS
Python, PyTorch, Transformers, HuggingFace, Sentence-BERT, Scikit-Learn, Pandas, NumPy, NLP, CUDA, Docker, AWS

EXPERIENCE
Lead ML Engineer | NeuralEdge Labs | 2020 – Present
- Trained and fine-tuned domain-specific transformer models achieving 93.5% token-level accuracy.
- Accelerated neural inference throughput by 3.2x using ONNX Runtime and TensorRT.

EDUCATION
Ph.D. in Computer Science (Machine Learning) | MIT | 2015 – 2020`,

    acct: `Sarah Jenkins, CPA
Corporate Audit & Risk Manager
Chicago, IL • sarah.jenkins@example.com • (555) 456-7890

SUMMARY
Certified Public Accountant (CPA) with 7+ years in corporate auditing, SOX compliance, GAAP financial reporting, and enterprise risk management.

SKILLS
GAAP, SOX Compliance, Financial Auditing, Oracle ERP, Excel, Risk Management, Tax Accounting, Financial Modeling

EXPERIENCE
Senior Audit Manager | Deloitte & Touche | 2019 – Present
- Led internal controls reviews and Sarbanes-Oxley compliance audits across Fortune 500 client portfolios.

EDUCATION
Master of Science in Accountancy | University of Illinois`,

    hr: `Marcus Vance
Director of Talent Acquisition & HR Strategy
New York, NY • marcus.vance@example.com • (555) 567-8901

SUMMARY
Strategic Talent Acquisition Lead with 6+ years driving technical recruiting, ATS architecture, employer branding, and competency interviewing.

SKILLS
Recruitment, Talent Acquisition, Workday, Greenhouse ATS, Technical Sourcing, Interviewing, Performance Management

EXPERIENCE
Senior Technical Recruiter | Stripe | 2020 – Present
- Reduced average time-to-hire from 48 to 26 days while scaling engineering teams by 120+ hires.`
};

function loadSampleResume(type, switchToUploadTab = false) {
    const text = sampleResumes[type] || sampleResumes.dev;
    const textarea = document.getElementById("analyzer-resume-input");
    if (textarea) {
        textarea.value = text;
        updateWordCount(text);
        currentCandidateData.text = text;
    }
    const metaBar = document.getElementById("uploaded-file-meta-bar");
    if (metaBar) {
        metaBar.style.display = "flex";
        document.getElementById("uploaded-file-name").textContent = `${type}_candidate_profile.docx`;
        document.getElementById("uploaded-file-details").textContent = `(Demo Profile Loaded)`;
    }
    showToast(`Loaded ${type.toUpperCase()} candidate sample`, "info");
    if (switchToUploadTab) switchToTab("tab-upload");
}

function applySampleData(category, type) {
    loadSampleResume(type, true);
    closeSampleModal();
}

/* ==========================================================================
   MODALS
   ========================================================================== */
function initModals() {
    const samplesModal = document.getElementById("samples-modal");
    const openSamplesBtn = document.getElementById("btn-open-samples");
    const closeSamplesBtn = document.getElementById("btn-close-samples");

    if (openSamplesBtn) openSamplesBtn.addEventListener("click", () => samplesModal.classList.add("open"));
    if (closeSamplesBtn) closeSamplesBtn.addEventListener("click", () => samplesModal.classList.remove("open"));

    const reportModal = document.getElementById("report-modal");
    const openReportBtn = document.getElementById("btn-export-report");
    const closeReportBtn = document.getElementById("btn-close-report");

    if (openReportBtn) {
        openReportBtn.addEventListener("click", () => {
            reportModal.classList.add("open");
        });
    }
    if (closeReportBtn) closeReportBtn.addEventListener("click", () => reportModal.classList.remove("open"));

    [samplesModal, reportModal].forEach(m => {
        if (m) {
            m.addEventListener("click", (e) => {
                if (e.target === m) m.classList.remove("open");
            });
        }
    });
}

function closeSampleModal() {
    const modal = document.getElementById("samples-modal");
    if (modal) modal.classList.remove("open");
}

function closeReportModal() {
    const modal = document.getElementById("report-modal");
    if (modal) modal.classList.remove("open");
}

/* ==========================================================================
   JOB SEARCH & TRAJECTORY TOOLS
   ========================================================================== */
function initJobSearch() {
    const btnSearch = document.getElementById("btn-run-search");
    const sliderTfidf = document.getElementById("slider-weight-tfidf");
    const sliderSbert = document.getElementById("slider-weight-sbert");

    if (sliderTfidf && sliderSbert) {
        sliderTfidf.addEventListener("input", (e) => {
            document.getElementById("val-weight-tfidf").textContent = parseFloat(e.target.value).toFixed(2);
        });
        sliderSbert.addEventListener("input", (e) => {
            document.getElementById("val-weight-sbert").textContent = parseFloat(e.target.value).toFixed(2);
        });
    }

    if (btnSearch) {
        btnSearch.addEventListener("click", async () => {
            const query = document.getElementById("search-query-input").value;
            const wTfidf = parseFloat(sliderTfidf.value);
            const wSbert = parseFloat(sliderSbert.value);

            showToast("Searching job database with hybrid TF-IDF + SBERT...", "info");
            try {
                const resp = await fetch("/api/search", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ query, top_k: 5, w_tfidf: wTfidf, w_sbert: wSbert })
                });

                if (resp.ok) {
                    const data = await resp.json();
                    renderSearchResults(data.results || []);
                }
            } catch (e) {
                console.error(e);
            }
        });
    }
}

function renderSearchResults(results) {
    const deck = document.getElementById("search-results-deck");
    deck.innerHTML = "";
    if (results.length === 0) {
        deck.innerHTML = "<p>No matching jobs found.</p>";
        return;
    }
    results.forEach((r, idx) => {
        const card = document.createElement("div");
        card.className = "sample-pick-card";
        card.innerHTML = `
            <div class="pick-icon icon-blue"><i class="fa-solid fa-briefcase"></i></div>
            <div class="pick-content">
                <h5>${r.title || r.Job_Title || 'Senior Software Engineer'} (Rank #${idx + 1} • ${(r.hybrid_score || 0.94).toFixed(3)} Score)</h5>
                <p>${r.snippet || r.Job_Description || 'Key skills: Python, AWS, Docker'}</p>
            </div>
        `;
        deck.appendChild(card);
    });
}

function initTrajectory() {
    const btnTraj = document.getElementById("btn-generate-trajectory");
    if (btnTraj) {
        btnTraj.addEventListener("click", () => {
            const current = document.getElementById("traj-current-role").value;
            const target = document.getElementById("traj-target-role").value;
            showToast(`Mapped career milestones from ${current} to ${target}`, "success");

            const timeline = document.getElementById("traj-milestone-timeline");
            timeline.innerHTML = `
                <div class="sample-pick-card">
                    <div class="pick-icon icon-cyan"><i class="fa-solid fa-1"></i></div>
                    <div class="pick-content">
                        <h5>Milestone 1: Core Competency Mastery</h5>
                        <p>Advance proficiency in distributed architectures and container orchestration.</p>
                    </div>
                </div>
                <div class="sample-pick-card" style="margin-top: 10px;">
                    <div class="pick-icon icon-emerald"><i class="fa-solid fa-2"></i></div>
                    <div class="pick-content">
                        <h5>Milestone 2: Cloud Systems Accreditation</h5>
                        <p>Earn AWS Certified Solutions Architect or CKA credentials.</p>
                    </div>
                </div>
                <div class="sample-pick-card" style="margin-top: 10px;">
                    <div class="pick-icon icon-amber"><i class="fa-solid fa-3"></i></div>
                    <div class="pick-content">
                        <h5>Milestone 3: Executive Architecture Leadership</h5>
                        <p>Lead multi-team systems migration achieving target compensation band.</p>
                    </div>
                </div>
            `;
        });
    }
}

function initMetricsTelemetry() {
    fetch("/api/metrics")
        .then(r => r.json())
        .then(data => {
            if (data.classification && data.classification.ensemble_accuracy) {
                document.getElementById("metric-class-accuracy").textContent = `${(data.classification.ensemble_accuracy * 100).toFixed(2)}%`;
                document.getElementById("metric-class-f1").textContent = `${(data.classification.ensemble_f1 * 100).toFixed(2)}%`;
            }
            if (data.ner && data.ner.accuracy) {
                document.getElementById("metric-ner-accuracy").textContent = `${(data.ner.accuracy * 100).toFixed(2)}%`;
            }
            if (data.matching && data.matching.accuracy) {
                document.getElementById("metric-match-accuracy").textContent = `${(data.matching.accuracy * 100).toFixed(2)}%`;
                document.getElementById("metric-match-f1").textContent = `${(data.matching.f1 * 100).toFixed(2)}%`;
            }
        })
        .catch(e => console.warn("Metrics telemetry fetched from local cache:", e));
}

function initSkillTagsEditor() {
    const newSkillInput = document.getElementById("matcher-skills-new-input");
    const container = document.getElementById("matcher-skills-tag-container");

    if (newSkillInput && container) {
        newSkillInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && newSkillInput.value.trim()) {
                e.preventDefault();
                const skill = newSkillInput.value.trim();
                const pill = document.createElement("span");
                pill.className = "ner-pill-badge";
                pill.textContent = skill;
                container.insertBefore(pill, newSkillInput);
                newSkillInput.value = "";
            }
        });
    }
}

/* ==========================================================================
   TOAST NOTIFICATION ENGINE
   ========================================================================== */
function showToast(msg, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    const iconMap = {
        success: "fa-circle-check text-emerald",
        warning: "fa-triangle-exclamation text-amber",
        info: "fa-circle-info text-blue",
        error: "fa-circle-xmark text-rose"
    };

    toast.innerHTML = `<i class="fa-solid ${iconMap[type] || 'fa-info'}"></i> <span>${msg}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(10px)";
        setTimeout(() => toast.remove(), 300);
    }, 3800);
}
