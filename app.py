# ============================================================
# 🤖 Interview Preparation Assistant (Groq + Serper + Streamlit)
# ============================================================

import os
import requests
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()  # reads .env from current directory

# --- Set API keys from environment ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not GROQ_API_KEY or not SERPER_API_KEY:
    st.error("❌ Missing API keys! Please check your .env file.")
    st.stop()

# --- Initialize Groq client ---
client = Groq(api_key=GROQ_API_KEY)

# --- Search company info using Serper.dev ---
def search_company_info(company_name: str, job_role: str) -> str:
    query = f"{company_name} {job_role} interview salary reviews company type"
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json",
    }
    data = {"q": query}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        results = response.json().get("organic", [])
    except Exception as e:
        st.error(f"⚠️ Error fetching company info: {e}")
        return ""

    if not results:
        return "No relevant info found."

    summary = []
    for item in results[:6]:
        title = item.get("title", "")
        link = item.get("link", "")
        snippet = item.get("snippet", "")
        summary.append(f"- [{title}]({link}) — {snippet}")

    return "\n".join(summary)

# --- Generate Interview Preparation Guide using Groq ---
def generate_interview_guide(company_name: str, job_role: str, facts: str) -> str:
    prompt = f"""
    You are an expert interview coach and career mentor helping a candidate prepare for a **{job_role}** role at **{company_name}**.

    Below are verified facts collected from online research:
    {facts}

    ### Task
    Create a **comprehensive interview preparation guide** in **Markdown format** with **clear headings, bullet points, and clickable links**.

    ### Content Requirements
    Cover the following sections **in detail**:

    ## 1. Company Overview
    - What {company_name} does (products, services, domain)
    - Business model and target customers
    - Company culture, mission, and recent achievements (if available)

    ## 2. Salary Expectations (India)
    - Average salary range for **{job_role}** in India
    - Entry-level, mid-level, and senior-level estimates
    - Mention sources (e.g., Glassdoor, AmbitionBox, Levels.fyi) with **links**

    ## 3. Company Locations
    - Headquarters location
    - Major offices in India and globally
    - Remote / hybrid work availability (if known)

    ## 4. Company Reviews & Work Culture
    - Summary of employee reviews
    - Pros and cons mentioned by employees
    - Ratings from websites like:
      - Glassdoor
      - AmbitionBox
      - Indeed  
      (Include **direct links**)

    ## 5. Frequently Asked Interview Questions (Role-Specific)
    - Technical questions related to **{job_role}**
    - Behavioral questions (HR round)
    - Managerial / scenario-based questions
    - Coding / system design / case study questions (if applicable)

    ## 6. Preparation Resources & Practice Websites
    Provide **clickable links** under each category:

    ### Technical Preparation
    - Official documentation
    - Tutorials, blogs, or courses
    - GitHub repositories (if relevant)

    ### Coding & Practice Platforms
    - LeetCode
    - HackerRank
    - CodeChef
    - GeeksforGeeks

    ### Interview Experience & Company-Specific Prep
    - Glassdoor interview experiences
    - AmbitionBox interview questions
    - Reddit / Medium posts (if relevant)

    ## 7. Final Summary (Easy-to-Understand)
    Conclude with **simple bullet points** covering:
    - What to focus on before the interview
    - How to prepare in the last 7 days
    - Key tips to stand out in the interview

    ### Style Guidelines
    - Use clear Markdown headings (##, ###)
    - Keep explanations simple and beginner-friendly
    - Ensure all external references are **clickable links**
    - Maintain a professional yet motivating tone

"""
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1024,
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"⚠️ Error generating guide: {e}")
        return ""

# --- Streamlit UI setup ---
st.set_page_config(page_title="Interview Prep AI", page_icon="🤖", layout="wide")

st.title("🤖 AI Interview Preparation Assistant")
st.markdown("This app used to know details about the Job and company reviews")

st.divider()

# --- Input form ---
with st.form("input_form"):
    company_name = st.text_input("🏢 Company Name", placeholder="e.g., Google")
    job_role = st.text_input("💼 Job Role", placeholder="e.g., Data Scientist")
    submitted = st.form_submit_button("Generate Interview Guide")

if submitted:
    if not company_name or not job_role:
        st.warning("⚠️ Please enter both a company name and a job role.")
        st.stop()

    # Step 1: Fetch web insights
    with st.spinner("🔍 Searching the web for company details..."):
        facts = search_company_info(company_name, job_role)

    if not facts:
        st.warning("No data found to generate guide.")
        st.stop()

    st.subheader("🌐 Web Insights")
    st.markdown(facts)

    # Step 2: Generate AI guide
    with st.spinner("🧠 Generating your AI-based interview preparation guide..."):
        guide = generate_interview_guide(company_name, job_role, facts)

    if guide:
        st.success("✅ Interview Preparation Guide Generated!")
        st.subheader("📘 AI Interview Guide")
        st.markdown(guide)

        # Download button
        st.download_button(
            label="📥 Download Guide as Text",
            data=guide,
            file_name=f"{company_name}_{job_role}_Interview_Guide.txt",
            mime="text/plain",
        )
