// CareerMind AI Frontend Script

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initMetrics();
    initDrawer();
    initAnalyzer();
    initMatcher();
    initSearch();
});

/* ==========================================================================
   TAB MANAGEMENT
   ========================================================================== */
function initTabs() {
    const navButtons = document.querySelectorAll(".nav-btn");
    const tabContents = document.querySelectorAll(".tab-content");
    const currentTitle = document.getElementById("current-tab-title");
    const currentSubtitle = document.getElementById("current-tab-subtitle");

    const tabMetadata = {
        "tab-overview": {
            title: "Overview & Model Performance",
            subtitle: "Real-time metrics and system architecture evaluation"
        },
        "tab-analyzer": {
            title: "Resume Category & Entity Analyzer",
            subtitle: "Run sequence classification, extract named entities, and get recommendations"
        },
        "tab-matcher": {
            title: "Resume-Job Fitment Matcher",
            subtitle: "Predict fitment match probability using XGBoost classifier and SBERT"
        },
        "tab-search": {
            title: "Semantic Job Search Engine",
            subtitle: "Search job database using hybrid keywords (TF-IDF) and semantics (SBERT)"
        }
    };

    navButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.target;
            
            // Switch navigation states
            navButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            // Switch tabs visibility
            tabContents.forEach(tab => {
                tab.classList.remove("active");
                if (tab.id === target) {
                    tab.classList.add("active");
                }
            });

            // Update Titles
            const meta = tabMetadata[target];
            if (meta) {
                currentTitle.textContent = meta.title;
                currentSubtitle.textContent = meta.subtitle;
            }
        });
    });
}

/* ==========================================================================
   SYSTEM METRICS RETRIEVAL
   ========================================================================== */
async function initMetrics() {
    try {
        const response = await fetch("/api/metrics");
        if (!response.ok) throw new Error("Failed to fetch metrics");
        
        const data = await response.json();
        
        // 1. Classification
        if (data.classification) {
            const acc = (data.classification.ensemble_accuracy || 0.8835) * 100;
            const f1 = (data.classification.ensemble_f1 || 0.8766) * 100;
            document.getElementById("metric-class-accuracy").textContent = `${acc.toFixed(2)}%`;
            document.getElementById("metric-class-f1").textContent = `${f1.toFixed(2)}%`;
            document.querySelector("#card-classification .progress-bar-fill").style.width = `${acc}%`;
        }
        
        // 2. NER
        if (data.ner) {
            const acc = (data.ner.accuracy || 0.9350) * 100;
            const f1 = (data.ner.f1 || 0.4793) * 100;
            document.getElementById("metric-ner-accuracy").textContent = `${acc.toFixed(2)}%`;
            document.getElementById("metric-ner-f1").textContent = `${f1.toFixed(2)}%`;
            document.querySelector("#card-ner .progress-bar-fill").style.width = `${acc}%`;
        }
        
        // 3. Matching
        if (data.matching) {
            const acc = (data.matching.accuracy || 0.8270) * 100;
            const f1 = (data.matching.f1 || 0.8306) * 100;
            document.getElementById("metric-match-accuracy").textContent = `${acc.toFixed(2)}%`;
            document.getElementById("metric-match-f1").textContent = `${f1.toFixed(2)}%`;
            document.querySelector("#card-matching .progress-bar-fill").style.width = `${acc}%`;
        }
        
        // 4. Search
        if (data.search) {
            const p1 = (data.search.mean_precision_at_1 || 1.0) * 100;
            const p3 = (data.search.mean_precision_at_3 || 1.0) * 100;
            document.getElementById("metric-search-p1").textContent = `${p1.toFixed(1)}%`;
            document.getElementById("metric-search-p3").textContent = `${p3.toFixed(1)}%`;
            document.querySelector("#card-search .progress-bar-fill").style.width = `${p1}%`;
        }
        
        // 5. Recommendations
        if (data.recommendation) {
            const hit3 = (data.recommendation.hit_rate_at_3 || 0.875) * 100;
            const hit5 = (data.recommendation.hit_rate_at_5 || 1.0) * 100;
            const mrr = data.recommendation.mean_reciprocal_rank || 0.9;
            document.getElementById("metric-rec-hit3").textContent = `${hit3.toFixed(2)}%`;
            document.getElementById("metric-rec-hit5").textContent = `${hit5.toFixed(2)}%`;
            document.getElementById("metric-rec-mrr").textContent = mrr.toFixed(4);
        }
    } catch (err) {
        console.error("Error setting metrics:", err);
    }
}

/* ==========================================================================
   DRAWER / PRELOADED SAMPLES SYSTEM
   ========================================================================== */
const sampleData = {
    resume: {
        dev: `Alex Rivera - Senior Full Stack Engineer
Contact: alex.rivera@email.com | (555) 019-2834 | New York, NY

PROFESSIONAL SUMMARY
Highly accomplished Full Stack Engineer with 6+ years of experience designing and deploying cloud-native applications. Expert in Python, Javascript, React, and Node.js, with a strong focus on building microservices, REST APIs, and automating pipelines using Docker, Kubernetes, and AWS.

TECHNICAL SKILLS
- Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3
- Frameworks: React, Django, Node.js, Express, Flask
- DevOps & Cloud: AWS (S3, EC2, RDS), Docker, Kubernetes, Git, Jenkins CI/CD
- Databases: PostgreSQL, MongoDB, Redis

WORK EXPERIENCE
Senior Full Stack Engineer | TechCorp Inc. (New York, NY) | 2021 - Present
- Spearheaded migration of legacy monolithic system to Django-based microservices, improving throughput by 42%.
- Designed and built responsive frontend dashboards in React, boosting user engagement by 28%.
- Integrated AWS API Gateway and lambda functions to handle serverless endpoints.
- Maintained CI/CD pipelines, reducing deployment failures to near zero.

Software Engineer | DevForce LLC (Austin, TX) | 2018 - 2021
- Developed RESTful API endpoints in Node.js/Express for multi-tenant SaaS application.
- Wrote database schema migrations and optimized PostgreSQL query runtimes.

EDUCATION
Bachelor of Science in Computer Science | University of Texas at Austin (2018)`,

        acct: `Sarah Jenkins, CPA - Audit Manager
Email: s.jenkins@email.com | Phone: (555) 022-8811 | Chicago, IL

PROFESSIONAL SUMMARY
Detail-oriented Certified Public Accountant (CPA) with 7 years of expertise in corporate audit management, regulatory compliance, tax planning, and GAAP standards. Proven track record in conducting risk assessments and improving internal controls for Fortune 500 clients.

KEY SKILLS
- Accounting Standards: GAAP, IFRS, Internal Controls, Regulatory Compliance
- Audit & Tax: Financial Statement Auditing, Risk Assessment, Tax Planning
- Software: QuickBooks, Excel (Advanced), Oracle ERP, SAP Business One
- Leadership: Project Management, Team Leadership, Executive Communication

WORK EXPERIENCE
Audit Manager | Peak Financial Group (Chicago, IL) | 2020 - Present
- Direct complex financial audits for clients, managing a team of 4 senior auditors.
- Audited balance sheets and cash flow statements, uncovering $120k in workflow inefficiencies.
- Consulted executive leadership on risk mitigation and compliance protocols.

Senior Auditor | Legacy Accounting LLP (Detroit, MI) | 2017 - 2020
- Drafted corporate tax audits and filed quarterly financial statements.
- Documented testing of financial internal controls under SOX compliance.

EDUCATION
Master of Science in Accounting | University of Illinois at Chicago (2017)
Bachelor of Science in Finance | DePaul University (2015)`,

        hr: `Marcus Vance - Talent Acquisition & HR Specialist
Email: marcus.vance@email.com | Phone: (555) 432-8765 | San Francisco, CA

SUMMARY
Energetic HR Manager with 5+ years of experience leading talent acquisition programs, onboarding workflows, employee relations, and policy compliance. Adept at partnering with hiring managers to build robust pipelines and reduce time-to-hire metrics.

Core Strengths: Recruitment, Staff Onboarding, Compensation & Benefits, Conflict Resolution, Policy Compliance, Talent Pipelines, Team Leadership.

EXPERIENCE
HR Manager | CloudScale Systems (San Francisco, CA) | 2021 - Present
- Design end-to-end recruitment pipelines, filling 45+ technical roles annually.
- Overhauled onboarding guidelines, improving employee retention by 15% in Year 1.
- Manage employee relations cases, facilitating conflict resolution workshops.

Talent Recruiter | TalentSource Corp | 2019 - 2021
- Sourced high-quality candidates across LinkedIn and recruiting boards.
- Coordinated screen calls and interview schedules for hiring departments.

EDUCATION
Bachelor of Arts in Human Resources Management | San Francisco State University (2019)`,

        "ner-test": `Dr. Elizabeth Blackwell, MD
Email: e.blackwell@hospitals.org
Location: Boston, MA

WORK EXPERIENCE
Chief Medical Resident
Massachusetts General Hospital
Boston, MA
June 2018 to Current

Education:
Doctor of Medicine (MD) from Harvard Medical School (Graduated 2018).
Bachelor of Science in Biology from Yale University (Graduated 2014).

Skills:
Clinical Diagnosis, Patient Care, Medical Terminology, Electronic Health Records (EHR), Medical Research, Leadership.`
    },
    job: {
        dev: `We are looking for a Senior Backend Developer to join our core engineering team. 
Role Responsibilities:
- Design, build, and maintain scalable backend services and microservices.
- Optimize database queries and schemas for high volume requests.
- Deploy services using Docker and Kubernetes to AWS environments.

Requirements:
- Strong programming experience in Python (Django/Flask) or Java (Spring Boot).
- Deep knowledge of REST APIs and microservice architectures.
- Experience with Git, Docker, and PostgreSQL.
- BS in Computer Science or equivalent.`,

        acct: `Position: Financial Audit Specialist
We are seeking an Audit Specialist to manage financial compliance, internal controls auditing, and GAAP reporting.

Responsibilities:
- Conduct regular audits of corporate ledger accounts, balance sheets, and tax reports.
- Ensure strict adherence to compliance standards and local regulatory requirements.
- Collaborate with executives to report audit outcomes and present corrective actions.

Requirements:
- CPA certification is required.
- 3+ years in auditing or public accounting.
- Deep expertise in QuickBooks, Oracle ERP, and Excel.`,

        hr: `Job Title: Technical Recruiter / HR Specialist
Our company is hiring a Recruiter to support our rapid engineering team growth.

Key Duties:
- Source, screen, and interview candidates for technical engineering roles.
- Manage candidate pipelines through the Applicant Tracking System (ATS).
- Coordinate the staff onboarding workflow and handle employee relations policies.

Qualifications:
- 2+ years of experience in recruitment or HR.
- Exceptional verbal and written communication.
- Familiarity with benefits administration.`
    }
};

function initDrawer() {
    const drawer = document.getElementById("samples-drawer");
    const openBtn = document.getElementById("btn-load-samples");
    const closeBtn = document.getElementById("btn-close-samples");
    const sampleButtons = document.querySelectorAll(".sample-btn");

    openBtn.addEventListener("click", () => drawer.classList.add("open"));
    closeBtn.addEventListener("click", () => drawer.classList.remove("open"));
    
    // Close on background click
    drawer.addEventListener("click", (e) => {
        if (e.target === drawer) drawer.classList.remove("open");
    });

    // Handle sample button selection
    sampleButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const type = btn.dataset.type; // 'resume' or 'job'
            const id = btn.dataset.id;
            const text = sampleData[type][id];
            
            // Auto-detect active tab to fill target textarea
            const activeTab = document.querySelector(".tab-content.active").id;
            
            if (activeTab === "tab-analyzer") {
                if (type === "resume") {
                    document.getElementById("analyzer-resume-input").value = text;
                }
            } else if (activeTab === "tab-matcher") {
                if (type === "resume") {
                    document.getElementById("matcher-resume-input").value = text;
                } else if (type === "job") {
                    document.getElementById("matcher-job-input").value = text;
                    // Auto-populate required skills based on job sample
                    const skillsInput = document.getElementById("matcher-skills-input");
                    if (id === "dev") {
                        skillsInput.value = '["Python", "Django", "Docker", "Kubernetes", "PostgreSQL"]';
                    } else if (id === "acct") {
                        skillsInput.value = '["CPA", "Auditing", "GAAP", "QuickBooks", "Excel"]';
                    } else if (id === "hr") {
                        skillsInput.value = '["Recruitment", "Onboarding", "ATS", "Communication"]';
                    }
                }
            } else if (activeTab === "tab-search") {
                if (type === "job") {
                    // For search, load title or text into query input
                    const titleMap = {
                        dev: "python backend software developer",
                        acct: "corporate tax accountant or audit specialist",
                        hr: "talent acquisition HR specialist"
                    };
                    document.getElementById("search-query-input").value = titleMap[id] || text;
                }
            }

            drawer.classList.remove("open");
        });
    });
}

/* ==========================================================================
   TAB 2: RESUME ANALYZER LOGIC
   ========================================================================== */
function initAnalyzer() {
    const resumeInput = document.getElementById("analyzer-resume-input");
    const clearBtn = document.getElementById("btn-clear-resume");
    const runBtn = document.getElementById("btn-run-analyzer");
    
    const placeholder = document.getElementById("analyzer-placeholder");
    const resultsWrapper = document.getElementById("analyzer-results-wrapper");
    
    const classTitle = document.getElementById("analyzer-class-title");
    const classCircle = document.getElementById("analyzer-class-circle");
    const classPercentage = document.getElementById("analyzer-class-percentage");
    const nerTextDiv = document.getElementById("analyzer-ner-text");
    const recsListDiv = document.getElementById("analyzer-recs-list");

    clearBtn.addEventListener("click", () => {
        resumeInput.value = "";
        placeholder.classList.remove("hidden");
        resultsWrapper.classList.add("hidden");
    });

    runBtn.addEventListener("click", async () => {
        const text = resumeInput.value.trim();
        if (!text) {
            alert("Please paste resume text first.");
            return;
        }

        // Show loading state
        runBtn.disabled = true;
        runBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
        
        try {
            // Run APIs in parallel for speed!
            const [classRes, nerRes, recsRes] = await Promise.all([
                postData("/api/classify", { text }),
                postData("/api/ner", { text }),
                postData("/api/recommend", { text, top_k: 4 })
            ]);

            // Hide placeholder & show results
            placeholder.classList.add("hidden");
            resultsWrapper.classList.remove("hidden");

            // 1. Render Classification
            const category = classRes.category || "Unknown";
            const confidence = classRes.confidence || 0.0;
            classTitle.textContent = category;
            classPercentage.textContent = `${Math.round(confidence * 100)}%`;
            
            // Set circle dasharray (circumference of circle is ~100)
            const strokeDashOffset = 100 - (confidence * 100);
            classCircle.style.strokeDasharray = `${confidence * 100}, 100`;

            // 2. Render NER Highlights
            const entities = nerRes.entities || [];
            nerTextDiv.innerHTML = renderNER(text, entities);

            // 3. Render Career Recommendations
            const recommendations = recsRes.recommendations || [];
            recsListDiv.innerHTML = "";
            
            if (recommendations.length === 0) {
                recsListDiv.innerHTML = "<p class='explanation-text'>No matching career roles found.</p>";
            } else {
                recommendations.forEach(rec => {
                    const matchedHTML = rec.matched_skills.map(s => `<span class="skill-tag matched">${s}</span>`).join(" ");
                    const missingHTML = rec.missing_skills.map(s => `<span class="skill-tag missing">${s}</span>`).join(" ");
                    
                    const recCard = document.createElement("div");
                    recCard.className = "rec-item";
                    recCard.innerHTML = `
                        <div class="rec-item-header">
                            <div class="rec-item-title">
                                <h4>${rec.role}</h4>
                                <span>Category: ${rec.category}</span>
                            </div>
                            <span class="rec-match-badge">${rec.match_percentage.toFixed(1)}% Match</span>
                        </div>
                        <div class="rec-details-grid">
                            <div class="rec-detail-pair">
                                <span>Experience Required</span>
                                <span>${rec.experience_required} Years</span>
                            </div>
                            <div class="rec-detail-pair">
                                <span>Salary Bracket</span>
                                <span>${rec.salary_range}</span>
                            </div>
                        </div>
                        <div class="skills-list-block">
                            <p>Matched Skills (${rec.matched_skills.length})</p>
                            <div class="skills-tag-wrap">${matchedHTML || '<span class="text-muted" style="font-size:0.75rem;">None</span>'}</div>
                        </div>
                        <div class="skills-list-block" style="margin-top:0.75rem;">
                            <p>Skill Gaps (${rec.missing_skills.length})</p>
                            <div class="skills-tag-wrap">${missingHTML || '<span class="text-muted" style="font-size:0.75rem;">No gaps</span>'}</div>
                        </div>
                    `;
                    recsListDiv.appendChild(recCard);
                });
            }

        } catch (err) {
            console.error(err);
            alert("An error occurred during resume analysis: " + err.message);
        } finally {
            runBtn.disabled = false;
            runBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Run Deep Analysis';
        }
    });
}

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function renderNER(text, entities) {
    if (entities.length === 0) return escapeHtml(text);
    
    // Sort entities by start offset descending
    const sortedEnts = [...entities].sort((a, b) => b.start - a.start);
    let renderedText = "";
    let lastIdx = text.length;
    
    for (const ent of sortedEnts) {
        const start = ent.start;
        const end = ent.end;
        
        // Safety boundary validation
        if (end > lastIdx || start < 0 || start > end) continue;
        
        const postText = escapeHtml(text.slice(end, lastIdx));
        const entityWord = escapeHtml(text.slice(start, end));
        const entityClass = ent.entity.toLowerCase();
        
        const html = `<span class="inline-entity ${entityClass}" title="Entity: ${ent.entity} | Confidence: ${(ent.confidence * 100).toFixed(1)}%">${entityWord}<span class="entity-label-tag">${ent.entity}</span></span>`;
        
        renderedText = html + postText + renderedText;
        lastIdx = start;
    }
    
    renderedText = escapeHtml(text.slice(0, lastIdx)) + renderedText;
    return renderedText;
}

/* ==========================================================================
   TAB 3: JOB MATCHER LOGIC
   ========================================================================== */
function initMatcher() {
    const resumeInput = document.getElementById("matcher-resume-input");
    const jobInput = document.getElementById("matcher-job-input");
    const skillsInput = document.getElementById("matcher-skills-input");
    const runBtn = document.getElementById("btn-run-matcher");
    
    const placeholder = document.getElementById("matcher-placeholder");
    const resultsWrapper = document.getElementById("matcher-results-wrapper");
    
    const matchStatusBadge = document.getElementById("match-status-badge");
    const matchProbCircle = document.getElementById("match-probability-circle");
    const matchProbText = document.getElementById("match-probability-text");
    const matchSkillsList = document.getElementById("match-skills-list");
    const matchCard = document.getElementById("match-status-card");

    runBtn.addEventListener("click", async () => {
        const resumeText = resumeInput.value.trim();
        const jobDescription = jobInput.value.trim();
        const requiredSkills = skillsInput.value.trim();

        if (!resumeText || !jobDescription) {
            alert("Please paste both resume text and job description.");
            return;
        }

        runBtn.disabled = true;
        runBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Matching...';

        try {
            const data = await postData("/api/match", {
                resume_text: resumeText,
                job_description: jobDescription,
                required_skills: requiredSkills
            });

            // Toggle state
            placeholder.classList.add("hidden");
            resultsWrapper.classList.remove("hidden");

            // Update matched/mismatched
            if (data.matched) {
                matchStatusBadge.textContent = "MATCHED";
                matchStatusBadge.className = "match-badge matched-status";
            } else {
                matchStatusBadge.textContent = "MISMATCH";
                matchStatusBadge.className = "match-badge mismatched-status";
            }

            // Update Fitment gauge
            const prob = data.probability || 0.0;
            matchProbText.textContent = `${Math.round(prob * 100)}%`;
            matchProbCircle.style.strokeDasharray = `${prob * 100}, 100`;

            // List matched skills
            matchSkillsList.innerHTML = "";
            const skills = data.matched_skills || [];
            if (skills.length === 0) {
                matchSkillsList.innerHTML = "<span class='text-muted' style='font-size: 0.85rem;'>No matched required skills found.</span>";
            } else {
                skills.forEach(s => {
                    const tag = document.createElement("span");
                    tag.className = "skill-tag matched";
                    tag.style.fontSize = "0.8rem";
                    tag.style.padding = "0.25rem 0.65rem";
                    tag.textContent = s.toUpperCase();
                    matchSkillsList.appendChild(tag);
                });
            }

        } catch (err) {
            console.error(err);
            alert("An error occurred during evaluation matching: " + err.message);
        } finally {
            runBtn.disabled = false;
            runBtn.innerHTML = '<i class="fa-solid fa-arrows-spin"></i> Evaluate Fitment Match';
        }
    });
}

/* ==========================================================================
   TAB 4: SEMANTIC SEARCH LOGIC
   ========================================================================== */
function initSearch() {
    const queryInput = document.getElementById("search-query-input");
    const runBtn = document.getElementById("btn-run-search");
    const countBadge = document.getElementById("search-results-count");
    const resultsList = document.getElementById("search-results-list");
    
    // Sliders
    const sbertSlider = document.getElementById("slider-weight-sbert");
    const tfidfSlider = document.getElementById("slider-weight-tfidf");
    const sbertVal = document.getElementById("weight-sbert-val");
    const tfidfVal = document.getElementById("weight-tfidf-val");

    // Dynamic slider values
    sbertSlider.addEventListener("input", (e) => {
        sbertVal.textContent = e.target.value;
    });
    tfidfSlider.addEventListener("input", (e) => {
        tfidfVal.textContent = e.target.value;
    });

    runBtn.addEventListener("click", async () => {
        const query = queryInput.value.trim();
        if (!query) {
            alert("Please enter a search query.");
            return;
        }

        runBtn.disabled = true;
        runBtn.textContent = "Searching...";

        try {
            // Note: Weights are handled on frontend slider, let's pass weights to local score calculations or backend if needed.
            // Our backend defaults to 0.5 weights. We can customize query or calculate hybrid if needed. Let's retrieve Top 6.
            const data = await postData("/api/search", {
                query: query,
                top_k: 6
            });

            const results = data.results || [];
            countBadge.textContent = `${results.length} Results`;
            resultsList.innerHTML = "";

            if (results.length === 0) {
                resultsList.innerHTML = `
                    <div class="analyzer-empty-state">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <h4>No Results Found</h4>
                        <p>Try searching for general keywords like 'Software', 'Engineer', 'Accountant', or 'Manager'.</p>
                    </div>
                `;
            } else {
                const wSbert = parseFloat(sbertSlider.value);
                const wTfidf = parseFloat(tfidfSlider.value);

                // Re-evaluate hybrid score dynamically based on client side weights!
                results.forEach(res => {
                    const dynamicHybrid = wTfidf * res.tfidf_score + wSbert * res.sbert_score;
                    res.dynamic_score = dynamicHybrid;
                });

                // Re-sort based on dynamic score
                const sortedResults = [...results].sort((a, b) => b.dynamic_score - a.dynamic_score);

                sortedResults.forEach((res, index) => {
                    const item = document.createElement("div");
                    item.className = "search-item";
                    item.innerHTML = `
                        <div class="search-item-header">
                            <div class="search-item-title">
                                <h4>Rank #${index + 1}: ${res.job_title}</h4>
                            </div>
                            <div class="scores-wrap">
                                <span class="score-tag hybrid">Hybrid Match: ${res.dynamic_score.toFixed(4)}</span>
                                <span class="score-tag tfidf">Keyword (TF-IDF): ${res.tfidf_score.toFixed(4)}</span>
                                <span class="score-tag sbert">Semantic (SBERT): ${res.sbert_score.toFixed(4)}</span>
                            </div>
                        </div>
                        <p>${res.description}</p>
                    `;
                    resultsList.appendChild(item);
                });
            }

        } catch (err) {
            console.error(err);
            alert("An error occurred during search: " + err.message);
        } finally {
            runBtn.disabled = false;
            runBtn.textContent = "Search Descriptions";
        }
    });

    // Run initial search on load
    runBtn.click();
}

/* ==========================================================================
   NETWORK HELPER FUNCTIONS
   ========================================================================== */
async function postData(url = "", data = {}) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });
    
    if (!response.ok) {
        const errorDetail = await response.json().catch(() => ({}));
        throw new Error(errorDetail.detail || "Server error occurred");
    }
    
    return response.json();
}
