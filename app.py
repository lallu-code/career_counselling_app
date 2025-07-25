# --- START OF THE COMPLETE app.py (Add Career Section Removed) ---

import streamlit as st
import json
import os
from collections import defaultdict

# --- Page Configuration (Global UI) ---
st.set_page_config(
    page_title="Career Counselling App",
    page_icon="assets/logo.png",
    layout="wide"
)

# --- Data Handling ---
DATA_FILE = "careers.json"
EXAM_DATA_FILE = "exams.json"

@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path): return {}
    with open(file_path, "r", encoding="utf-8") as file:
        try: return json.load(file)
        except json.JSONDecodeError: return {}

# --- Helper function to get a flat dictionary of all careers ---
def get_all_careers(data):
    all_careers = {}
    for field, careers_in_field in data.items():
        for career in careers_in_field:
            all_careers[career['name']] = career
    return all_careers

# --- Page Navigation and State Management ---
def set_page(page_name, career_name=None):
    st.session_state.page = page_name
    if career_name:
        st.session_state.selected_career = career_name

# --- UI Components for each Page ---
def career_card(career_name, details):
    with st.container(border=True):
        st.markdown(f"### {career_name}")
        st.markdown(f"**Level:** `{details.get('level', 'N/A')}`")
        st.markdown(f"**Common Degrees:** `{details.get('degrees', 'N/A')}`")
        st.write(f"{details.get('description', 'No description available.')[:100]}...")
        if st.button("View Details", key=f"details_{career_name}", use_container_width=True):
            set_page("View Career Details", career_name=career_name)

def home_page(data):
    st.subheader("🎓 Explore Career Fields")
    if not data: return st.info("The career data file is empty.")
    
    fields = list(data.keys())
    selected_field = st.selectbox("Select a Field to Explore:", fields)
    
    st.divider()

    if selected_field:
        st.header(selected_field)
        careers_in_field = data[selected_field]
        
        level_filter = st.radio("Filter by level:", ("All", "Graduate", "Postgraduate"), horizontal=True, key=f"filter_{selected_field}")
        
        filtered_careers = []
        if level_filter == "All":
            filtered_careers = careers_in_field
        else:
            filtered_careers = [c for c in careers_in_field if c.get('level') == level_filter]

        if not filtered_careers:
            st.warning(f"No {level_filter.lower()} level careers found in {selected_field}.")
            return

        cols = st.columns(min(len(filtered_careers), 3))
        for i, career in enumerate(filtered_careers):
            with cols[i % 3]:
                career_card(career['name'], career)

def view_career_details(all_careers_data):
    st.subheader("🔍 Career Details")
    career_list = sorted(list(all_careers_data.keys()))
    if not career_list: return st.warning("No careers found.")
    
    default_index = 0
    if "selected_career" in st.session_state and st.session_state.selected_career in career_list:
        default_index = career_list.index(st.session_state.selected_career)
        
    selected = st.selectbox("Select a career to view", career_list, index=default_index, key="details_selectbox")
    st.divider()
    details = all_careers_data[selected]
    st.header(selected)
    st.markdown(f"**Level:** `{details.get('level', 'N/A')}` | **Common Degrees:** `{details.get('degrees', 'N/A')}`")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["**📝 Overview**", "**💼 Opportunities**", "**🛠️ Skills**", "**🗺️ Roadmap**", "**📚 Resources**"])
    
    with tab1:
        st.subheader("Description"); st.write(details.get('description', 'N/A'))
        st.subheader("Associated Tags")
        tags = details.get('tags', [])
        if tags:
            tags_html = "".join([f"<span style='background-color: #f0f2f6; border: 1px solid #dfe3e8; border-radius: 16px; padding: 4px 10px; margin: 4px 2px; display: inline-block;'>{tag}</span>" for tag in tags])
            st.markdown(tags_html, unsafe_allow_html=True)
        else: st.write("No tags available.")
        st.subheader("Future Prospects"); st.info(details.get('future_prospects', 'N/A'))

    with tab2:
        st.subheader("Salary")
        st.metric(label="Average Range (INR)", value=details.get('salary_inr', 'N/A'))
        
        st.divider()
        
        st.subheader("Common Opportunities")
        opportunities = details.get('opportunities', [])
        if opportunities:
            for opportunity in opportunities:
                st.markdown(f"- {opportunity}")
        else:
            st.info("No specific opportunities have been listed for this career.")
        
    with tab3:
        st.subheader("Key Skills for Success")
        skills = details.get('skills', {})
        if skills:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("##### ❤️ Soft Skills (Interpersonal)")
                for skill in skills.get('soft_skills', []): st.markdown(f"- {skill}")
            with col2:
                st.markdown("##### 🧠 Hard Skills (Technical)")
                for skill in skills.get('hard_skills', []): st.markdown(f"- {skill}")
        else:
            st.write("No skills data available.")
            
    with tab4:
        st.subheader(f"Typical Path to Becoming a {selected}")
        for i, step in enumerate(details.get('roadmap', []), 1):
            st.markdown(f"**Step {i}:** {step}")

    with tab5:
        st.subheader("Learning Resources & Links")
        resources = details.get('resources', {})
        if not resources:
            st.info("No specific resources have been added for this career yet.")
        else:
            if 'online_course' in resources:
                st.markdown(f"**🎓 Recommended Course:** [{resources['online_course']['name']}]({resources['online_course']['url']})")
            if 'youtube_channel' in resources:
                st.markdown(f"**📺 Key YouTube Channel:** [{resources['youtube_channel']['name']}]({resources['youtube_channel']['url']})")
            if 'must_read_book' in resources:
                st.markdown(f"**📖 Must-Read Book:** [{resources['must_read_book']['name']}]({resources['must_read_book']['url']})")
            if 'professional_body' in resources:
                st.markdown(f"**🏛️ Professional Body:** [{resources['professional_body']['name']}]({resources['professional_body']['url']})")

def quiz_page(all_careers_data):
    st.subheader("✨ Find Your Perfect Career")
    st.write("Answer these questions to discover careers that match your personality and interests.")
    questions = [
        {"question": "🧠 Which subject area do you enjoy the most?", "key": "q1", "options": {"Science & Math (Physics, Logic, Numbers)": ["Math", "Science", "Analytical", "Logical"], "Arts & Humanities (History, Literature, Languages)": ["Humanities", "Reading", "Writing", "Communicating"], "Creative Arts (Drawing, Design, Music)": ["Creative", "Design", "Art", "Visualisation"], "Business & Finance (Economics, Accounting)": ["Finance", "Business", "Management", "Structured"]}},
        {"question": "🤔 When faced with a complex problem, what is your first instinct?", "key": "q2", "options": {"Create a structured plan and follow it step-by-step.": ["Logical", "Structured", "Problem-Solving", "Detail-Oriented"], "Brainstorm creative and unconventional solutions.": ["Creative", "Innovation", "Visualisation", "Design"], "Research deeply to understand every aspect before acting.": ["Researching", "Reading", "Analytical", "Deep-Thinking"]}},
        {"question": "⚡ What kind of activity energizes you the most?", "key": "q3", "options": {"Building or creating something tangible (a product, a building, a program).": ["Building", "Creative", "Technology", "Hands-On"], "Helping or guiding people directly to improve their lives.": ["Helping", "Empathy", "Communicating", "Social-Impact"], "Organizing projects and leading a team towards a common goal.": ["Leadership", "Teamwork", "Management", "Strategic"]}},
        {"question": "🏢 Which work environment sounds most appealing?", "key": "q4", "options": {"A fast-paced, high-stakes environment where I have to make quick decisions.": ["High-Pressure", "Decision-Making", "Adventure", "Adaptability"], "A calm, predictable setting where I can focus deeply on my work.": ["Independent", "Deep-Thinking", "Structured", "Patience"], "A busy, social environment with lots of meetings and team collaboration.": ["Teamwork", "Communicating", "Extroverted", "Business"]}}
    ]
    if 'quiz_results' not in st.session_state: st.session_state.quiz_results = None
    if not st.session_state.quiz_results:
        with st.form("quiz_form"):
            user_answers = {}
            for q in questions: user_answers[q["key"]] = st.radio(q["question"], list(q["options"].keys()), key=q["key"])
            submitted = st.form_submit_button("Get My Recommendation!")
        if submitted:
            scores = defaultdict(int); user_tags = []
            for q in questions: user_tags.extend(q["options"][user_answers[q["key"]]])
            for career_name, details in all_careers_data.items():
                career_tags = set(details.get("tags", [])); score = len(set(user_tags) & career_tags); scores[career_name] = score
            sorted_careers = sorted(scores.items(), key=lambda item: item[1], reverse=True); st.session_state.quiz_results = (sorted_careers[:3], user_tags); st.rerun()
    if st.session_state.quiz_results:
        st.divider(); st.subheader("🌟 Your Top Career Recommendations")
        top_3, user_tags = st.session_state.quiz_results
        if not top_3 or top_3[0][1] == 0:
            st.warning("We couldn't find a strong match. Feel free to retake the quiz or explore careers on the 'Home' page!")
        else:
            for career_name, score in top_3:
                with st.container(border=True):
                    details = all_careers_data[career_name]; common_tags = set(user_tags) & set(details.get("tags", [])); match_percentage = int((score / len(user_tags)) * 100) if user_tags else 0
                    st.markdown(f"### {career_name}"); st.progress(match_percentage, text=f"{match_percentage}% Match")
                    if common_tags: st.markdown(f"**Recommended because it matches your interest in:** `{'`, `'.join(common_tags)}`")
                    st.write(f"{details.get('description', '')[:120]}..."); 
                    if st.button("Learn More", key=f"quiz_details_{career_name}", use_container_width=True): set_page("View Career Details", career_name=career_name)
        if st.button("Retake Quiz", type="primary"): st.session_state.quiz_results = None; st.rerun()

def compare_careers_page(all_careers_data):
    st.subheader("⚖️ Compare Careers"); st.write("Select 2 or 3 careers to see a side-by-side comparison.")
    options = sorted(list(all_careers_data.keys())); 
    selected_careers = st.multiselect("Select careers to compare", options, max_selections=3, placeholder="Choose up to 3 careers")
    if len(selected_careers) >= 2:
        st.divider(); cols = st.columns(len(selected_careers))
        for i, career_name in enumerate(selected_careers):
            with cols[i]:
                with st.container(border=True):
                    details = all_careers_data[career_name]
                    st.header(career_name)
                    st.markdown("---")
                    st.markdown("##### 💵 Salary")
                    st.metric(label="INR Range", value=details.get('salary_inr', 'N/A'))
                    st.markdown("---")
                    st.markdown("##### 🛠️ Top Hard Skills")
                    for skill in details.get('skills', {}).get('hard_skills', [])[:3]: st.markdown(f"- {skill}")
                    st.markdown("---")
                    st.markdown("##### 🗺️ First Step on Roadmap")
                    st.info(details.get('roadmap', ["N/A"])[0])

def exam_explorer_page():
    st.subheader("🎓 College & Exam Explorer")
    st.write("Discover key entrance exams and top colleges for major career streams in India.")
    exam_data = load_data(EXAM_DATA_FILE)
    if not exam_data: 
        st.error(f"The `{EXAM_DATA_FILE}` file was not found or is empty. Please create it."); return
    streams = list(exam_data.keys())
    selected_stream = st.selectbox("Select a Career Stream:", streams)
    st.divider()
    if selected_stream:
        st.header(f"Major Exams for {selected_stream}")
        exams = exam_data[selected_stream]
        for exam in exams:
            with st.expander(f"**{exam['name']}** - {exam['full_name']}"):
                st.write(exam['info'])
                st.markdown(f"**Top Colleges:** {', '.join(exam['colleges'])}")
                st.markdown(f"**[Official Website ➔]({exam['website']})**")

# --- MAIN APP LOGIC ---
def main():
    st.title("Career Counselling App")
    
    if "page" not in st.session_state:
        st.session_state.page = "Home"

    with st.sidebar:
        st.image("assets/logo.png", use_container_width=True)
        st.header("Menu")
        PAGES = {
            "Home": home_page,
            "✨ Career Recommender": quiz_page,
            "View Career Details": view_career_details,
            "Compare Careers": compare_careers_page,
            "🎓 College & Exam Explorer": exam_explorer_page,
            # "Add a New Career" page has been removed from this list
        }
        for page_name in PAGES.keys():
            if st.button(page_name, use_container_width=True, type=("primary" if st.session_state.page == page_name else "secondary")):
                set_page(page_name)
        st.divider()
        st.info("Select a field to explore careers or take the quiz for a personalized recommendation.")

    career_data = load_data(DATA_FILE)
    page_to_show = st.session_state.page
    page_function = PAGES.get(page_to_show)

    if page_function:
        if page_to_show == "Home":
            page_function(career_data)
        elif page_to_show == "🎓 College & Exam Explorer":
            page_function()
        else:
            all_careers = get_all_careers(career_data)
            page_function(all_careers)

if __name__ == "__main__":
    main()

# --- END OF FILE ---