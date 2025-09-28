# ui/app.py - Complete Enhanced Version
import streamlit as st
import sys
import os
import json
from datetime import datetime
import pandas as pd
import time
from netherlands_map import create_job_map
from streamlit_folium import st_folium
# Fix paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.join(parent_dir, 'src'))

from database.enhanced_database import JobDatabase
from analyzers.analyzer_ai import AIJobAnalyzer
from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.smart_description_enricher import SmartDescriptionEnricher

def apply_with_feedback(db, job_id):
    """Apply to job with visual feedback"""
    with st.spinner("Submitting application..."):
        db.conn.execute("UPDATE jobs SET status = 'applied', applied_at = ? WHERE id = ?", 
                       (datetime.now().isoformat(), job_id))
        db.conn.commit()
        st.success("✅ Applied successfully!")
        st.balloons()
        
st.set_page_config(
    page_title="AI Job Search Platform", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    db_path = os.path.join(parent_dir, 'data', 'jobs.db')
    return {
        'db': JobDatabase(db_path=db_path),
        'analyzer': AIJobAnalyzer(),
        'scraper': LinkedInScraper(),
        'enricher': SmartDescriptionEnricher()
    }

components = init_components()
db = components['db']
analyzer = components['analyzer']
scraper = components['scraper']
enricher = components['enricher']

# Custom CSS for better UI
st.markdown("""
<style>
     /* Dark mode colors */
    :root {
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
    }
    
    /* Typography improvements */
    h2 { margin-bottom: 0.5rem !important; }
    h3 { margin-top: 1.5rem !important; }
    
    /* Better buttons */
    div[data-testid="stButton"] button {
        transition: all 0.2s ease;
    }
    
    div[data-testid="stButton"] button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .stColumns { flex-direction: column !important; }
    }
    
    .job-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        color: white;
    }
    .score-high {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: white;
        font-weight: bold;
    }
    .score-medium {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: white;
        font-weight: bold;
    }
    .score-low {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffd93d 100%);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: white;
        font-weight: bold;
    }
     .job-title {
        font-size: 1.5rem;
        font-weight: 600;
        line-height: 1.2;
        margin-bottom: 0.5rem;
    }
    
    .company-name {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 1rem;
    }
    
    /* Button Hierarchy (Primary/Secondary/Tertiary) */
    .btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        padding: 12px 24px;
        border: none;
        box-shadow: 0 4px 14px 0 rgba(102, 126, 234, 0.4);
    }
    
    .btn-secondary {
        background: transparent;
        border: 2px solid #667eea;
        color: #667eea;
        padding: 10px 20px;
    }
    
    /* Score Badge Redesign */
    .score-badge {
        position: absolute;
        top: 1rem;
        right: 1rem;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .score-high { color: #10b981; }
    .score-medium { color: #f59e0b; }
    .score-low { color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# Sidebar - Control Center
with st.sidebar:
    st.title("🎯 Job Search")
    stats = db.get_statistics()
    # Progressive Disclosure - Show only essential controls
    with st.expander("Search Settings", expanded=True):
        search_terms = st.text_area("Keywords", value="Python Developer", height=60)
        location = st.text_input("Location", value="Netherlands")
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("🔍 Search", type="primary", use_container_width=True)
        with col2:
            st.button("🎲 AI Suggest", use_container_width=True)
    
    # Status at a glance
    st.metric("Ready to Apply", f"{stats['high_matches']}")
    st.metric("Total Reviewed", f"{stats['analyzed']}/{stats['total']}")
    
    # Advanced options hidden
    with st.expander("Advanced Actions"):
        st.button("🔄 Enrich Descriptions")
        st.button("🧠 Analyze All")
        st.button("🗑️ Clear Database")        
# Main Content Area
st.title("🚀 AI Job Search Platform")

# Tabs for different views
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Top Matches", 
    "📋 All Jobs", 
    "✉️ Applications", 
    "💬 AI Chat", 
    "📈 Analytics",
    "🗺️ Location Map"
])

with tab1:
    st.header("Your Top Job Matches")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        min_score = st.slider("Minimum Score", 0, 100, 70)
    with col2:
        status_filter = st.selectbox("Status", ["All", "New", "Applied", "Interview", "Rejected"])
    with col3:
        sort_by = st.selectbox("Sort By", ["Score", "Date", "Company"])
    
    # Get filtered jobs
    jobs = db.get_jobs_by_score(min_score)
    
    
    if not jobs:
        st.markdown("""
            <div style='text-align: center; padding: 4rem; background: #1e293b; border-radius: 12px;'>
                <h2>🔍 No matches found</h2>
                <p style='color: #94a3b8; margin: 1rem 0;'>
                    No jobs match your criteria yet. Try:
                </p>
                <ul style='text-align: left; display: inline-block;'>
                    <li>Lowering the minimum score filter</li>
                    <li>Scraping new jobs with different search terms</li>
                    <li>Running "Analyze All Jobs" to score unanalyzed positions</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    else:
        for job in jobs:
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Enhanced title and company display
                    st.markdown(f"<h2 style='margin-bottom: 0.5rem; font-size: 1.8rem;'>{job['title']}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<p style='color: #94a3b8; font-size: 1.1rem; margin-bottom: 1rem;'>{job['company']} • 📍 {job['location']}</p>", unsafe_allow_html=True)
                    
                    # Score badge with better styling
                    score = job['ai_score']
                    if score >= 85:
                        st.markdown(f'<span class="score-high" style="font-size: 1.5rem; font-weight: 700;">Match Score: {score}/100</span>', unsafe_allow_html=True)
                    elif score >= 75:
                        st.markdown(f'<span class="score-medium" style="font-size: 1.5rem; font-weight: 700;">Match Score: {score}/100</span>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<span class="score-low" style="font-size: 1.5rem; font-weight: 700;">Match Score: {score}/100</span>', unsafe_allow_html=True)
                    
                    # Disqualification check (keep your existing logic)
                    if job.get('disqualified'):
                        reasons = job.get('disqualification_reasons', '')
                        if isinstance(reasons, str) and reasons:
                            reasons = json.loads(reasons) if reasons.startswith('[') else [reasons]
                        elif isinstance(reasons, list):
                            pass
                        else:
                            reasons = ['Requirements not met']
                        
                        st.error("⛔ **You don't qualify for this position:**")
                        for reason in reasons:
                            st.write(f"   • {reason}")
                    
                    # Strengths and Concerns - cleaner layout
                    if job['ai_strengths'] or job['ai_concerns']:
                        str_col, con_col = st.columns(2)
                        
                        with str_col:
                            st.success("💪 **Top Strengths**")
                            strengths = json.loads(job['ai_strengths'] or '[]')
                            for s in strengths[:2]:  # Show only top 2
                                st.markdown(f"✓ {s}")
                        
                        with con_col:
                            st.warning("⚠️ **Key Concerns**")
                            concerns = json.loads(job['ai_concerns'] or '[]')
                            for c in concerns[:2]:  # Show only top 2
                                st.markdown(f"• {c}")
                    
                    # Detailed Analysis expandable
                    if job['ai_fit_assessment']:
                        with st.expander("📝 Detailed Analysis"):
                            st.write("**Why this is a match:**")
                            st.write(job['ai_fit_assessment'])
                            
                            if job['ai_recommendation']:
                                st.write("**Application Strategy:**")
                                st.write(job['ai_recommendation'])
                
                with col2:
                    st.markdown("### Actions")
                    
                    # Primary Action - Apply Now
                    if job.get('application_link'):
                        st.link_button("🚀 Apply Now", job['application_link'], use_container_width=True, type="primary")
                    else:
                        if st.button("✅ Apply", key=f"apply_{job['id']}", use_container_width=True, type="primary"):
                            db.conn.execute("UPDATE jobs SET status = 'applied', applied_at = ? WHERE id = ?", 
                                        (datetime.now().isoformat(), job['id']))
                            db.conn.commit()
                            st.success("Marked as applied!")
                            st.balloons()
                    
                    # Cover Letter Generation
                    cover_key = f"cover_btn_{job['id']}"
                    if st.button("📝 Cover Letter", key=cover_key, use_container_width=True):
                        with st.spinner("Generating personalized cover letter..."):
                            analysis = {
                                'score': job.get('ai_score', 0),
                                'strengths': json.loads(job.get('ai_strengths', '[]')),
                                'concerns': json.loads(job.get('ai_concerns', '[]')),
                                'fit_assessment': job.get('ai_fit_assessment', ''),
                                'recommendation': job.get('ai_recommendation', '')
                            }
                            
                            cover = analyzer.generate_cover_letter(job, analysis)
                            
                            st.text_area(
                                "Generated Cover Letter",
                                value=cover,
                                height=300,
                                key=f"cover_display_{job['id']}"
                            )
                            
                            st.download_button(
                                label="📥 Download",
                                data=cover,
                                file_name=f"cover_letter_{job['company']}_{job['title'].replace(' ', '_')}.txt",
                                mime="text/plain",
                                key=f"download_{job['id']}"
                            )
                    
                    # Secondary Actions
                    st.link_button("🔗 Open Job", job['url'], use_container_width=True)
                    
                    # Get Apply Link if not available
                    if not job.get('application_link'):
                        if st.button("🔗 Get Apply Link", key=f"getlink_{job['id']}", use_container_width=True):
                            with st.spinner("Fetching apply link..."):
                                apply_link = enricher.get_apply_link(job['url'])
                                db.update_apply_link(job['id'], apply_link)
                                st.rerun()
                    
                    # Tertiary Actions in expander
                    with st.expander("More Options"):
                        if st.button("👁️ View Details", key=f"view_{job['id']}", use_container_width=True):
                            st.session_state[f'show_job_{job["id"]}'] = True
                        
                        if st.button("❌ Not Interested", key=f"skip_{job['id']}", use_container_width=True):
                            db.conn.execute("UPDATE jobs SET status = 'skipped' WHERE id = ?", (job['id'],))
                            db.conn.commit()
                            st.rerun()
                
                # Show cover letter if it's in session state
                if st.session_state.get(f'cover_{job["id"]}'):
                    st.text_area("Generated Cover Letter", 
                            st.session_state[f'cover_{job["id"]}'], 
                            height=300)
                
                st.divider()
  
with tab2:
    st.header("All Jobs Database")
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Select All High Scores (80+)"):
            st.session_state['bulk_select'] = db.conn.execute(
                "SELECT id FROM jobs WHERE ai_score >= 80"
            ).fetchall()
    
    with col2:
        if st.button("Bulk Apply Selected"):
            if 'bulk_select' in st.session_state:
                for job_id in st.session_state['bulk_select']:
                    db.conn.execute(
                        "UPDATE jobs SET status = 'applied', applied_at = ? WHERE id = ?",
                        (datetime.now().isoformat(), job_id[0])
                    )
                db.conn.commit()
                st.success(f"Applied to {len(st.session_state['bulk_select'])} jobs!")
    
    # Job table
    jobs_df = pd.DataFrame(db.conn.execute(
        "SELECT title, company, location, ai_score, status, scraped_at FROM jobs ORDER BY ai_score DESC"
    ).fetchall())
    
    if not jobs_df.empty:
        jobs_df.columns = ['Title', 'Company', 'Location', 'Score', 'Status', 'Scraped']
        st.dataframe(jobs_df, use_container_width=True, height=600)

with tab3:
    st.header("Application Tracker")
    
    applied_jobs = db.conn.execute(
        "SELECT * FROM jobs WHERE status = 'applied' ORDER BY applied_at DESC"
    ).fetchall()
    
    if applied_jobs:
        for job in applied_jobs:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{job['title']}** at {job['company']}")
                st.write(f"Applied: {job['applied_at'][:10] if job['applied_at'] else 'Unknown'}")
            
            with col2:
                response = st.selectbox(
                    "Response", 
                    ["Waiting", "Rejected", "Interview", "Offer"],
                    key=f"response_{job['id']}"
                )
                if st.button("Update", key=f"update_{job['id']}"):
                    db.conn.execute(
                        "UPDATE jobs SET response_type = ? WHERE id = ?",
                        (response, job['id'])
                    )
                    db.conn.commit()
            
            with col3:
                if st.button("Add Note", key=f"note_{job['id']}"):
                    st.session_state[f'show_note_{job["id"]}'] = True
            
            if st.session_state.get(f'show_note_{job["id"]}'):
                note = st.text_area("Note", key=f"note_text_{job['id']}")
                if st.button("Save Note", key=f"save_note_{job['id']}"):
                    db.conn.execute(
                        "UPDATE jobs SET notes = ? WHERE id = ?",
                        (note, job['id'])
                    )
                    db.conn.commit()
                    st.success("Note saved!")
            
            st.divider()

with tab4:
    st.header("AI Career Assistant")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your job search..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Get context about jobs
                context = {
                    'total_jobs': db.conn.execute("SELECT COUNT(*) FROM jobs").fetchone()[0],
                    'top_matches': db.get_jobs_by_score(80),
                    'applied': db.conn.execute("SELECT COUNT(*) FROM jobs WHERE status = 'applied'").fetchone()[0]
                }
                
                # Generate response using Claude
                response = analyzer.chat_response(prompt, context)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

with tab5:
    st.header("Analytics Dashboard")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_score = db.conn.execute("SELECT AVG(ai_score) FROM jobs WHERE ai_score IS NOT NULL").fetchone()[0]
        st.metric("Average Match Score", f"{avg_score:.1f}" if avg_score else "N/A")
    
    with col2:
        high_matches = db.conn.execute("SELECT COUNT(*) FROM jobs WHERE ai_score >= 80").fetchone()[0]
        st.metric("High Matches (80+)", high_matches)
    
    with col3:
        response_rate = db.conn.execute(
            "SELECT COUNT(*) * 100.0 / COUNT(*) FROM jobs WHERE status = 'applied' AND response_type IS NOT NULL"
        ).fetchone()[0]
        st.metric("Response Rate", f"{response_rate:.1f}%" if response_rate else "0%")
    
    with col4:
        interviews = db.conn.execute("SELECT COUNT(*) FROM jobs WHERE response_type = 'Interview'").fetchone()[0]
        st.metric("Interviews", interviews)
    
    # Charts
    st.subheader("Score Distribution")
    scores = db.conn.execute("SELECT ai_score FROM jobs WHERE ai_score IS NOT NULL").fetchall()
    if scores:
        import pandas as pd
        df = pd.DataFrame(scores, columns=['Score'])
        st.bar_chart(df['Score'].value_counts().sort_index())

with tab6:
    st.header("Job Distribution Map")
    
    # Legend
    col1, col2, col3, col4 = st.columns(4)
    col1.success("🟢 High Score (80+)")
    col2.warning("🟠 Medium Score (70-79)")
    col3.error("🔴 Low Score (<70)")
    col4.info("⚫ No Jobs")
    
    # Create and display map
    try:
        job_map = create_job_map(db)
        map_data = st_folium(job_map, width=900, height=600)
        
        # If a location was clicked, offer to filter jobs
        if map_data['last_object_clicked']:
            clicked_popup = map_data['last_object_clicked'].get('popup', '')
            if clicked_popup:
                city_name = clicked_popup.split('<b>')[1].split('</b>')[0]
                if st.button(f"Filter jobs in {city_name}"):
                    st.session_state['location_filter'] = city_name
                    st.rerun()
    except Exception as e:
        st.error(f"Error loading map: {e}")

# Footer
st.markdown("---")
st.caption("AI Job Search Platform v1.0 | Powered by Claude API")