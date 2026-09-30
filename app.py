
import streamlit as st
from database import create_table, add_item, get_items
from matcher import calculate_matches
import os
import uuid
from database import add_image_column

st.set_page_config(
    page_title="ReFind",
    page_icon="🔎",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: #F4F8F6;
    }

    h1, h2, h3 {
        color: #125C50;
        font-family: 'Segoe UI', sans-serif;
    }

    [data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #D8EAE2;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
    }

    div.stButton > button[kind="primary"] {
        background-color: #16866D;
        color: white;
        border-radius: 10px;
        border: none;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #125C50;
        color: white;
    }

    [data-testid="stSidebar"] {
        background-color: #E5F0EB;
    }

    [data-testid="stFileUploader"] {
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)
# Initialize database
create_table()

add_image_column()

os.makedirs("images", exist_ok=True)

st.title("🔎 ReFind")
st.subheader(
    "Find what you've lost. Reconnect what you've found."
)

st.write(
    "An intelligent lost-and-found platform "
    "for college students."
)

st.divider()

def navigate_to(destination):
    st.session_state["navigation"] = destination

pages = [
    "Home",
    "Report Lost",
    "Report Found",
    "View Reports",
    "Find Matches"
]

if "navigation" not in st.session_state:
    st.session_state["navigation"] = "Home"

page = st.sidebar.radio(
    "Navigation",
    pages,
    key="navigation"
)
    
if page == "Home":

    st.markdown("""
    <div style="
        background: linear-gradient(120deg, #125C50, #229A7C);
        padding: 45px;
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
    ">
        <p style="color:#D8F4E7; font-weight:bold;">
            SMART CAMPUS SOLUTION
        </p>
        <h1 style="color:white; font-size:44px;">
            Welcome to ReFind.
        </h1>
        <p style="font-size:19px; color:#E5F8F0;">
            Lost something? Let's find it together.
        </p>
        <p style="color:#E5F8F0;">
            Report lost items, help others recover
            their belongings, and discover potential
            matches using intelligent NLP.
        </p>
    </div>
    """, unsafe_allow_html=True)

    lost_items = get_items("Lost")
    found_items = get_items("Found")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("🔍 Lost Reports", len(lost_items))

    with col2:
        st.metric("📦 Found Reports", len(found_items))

    with col3:
        st.metric(
            "📋 Total Reports",
            len(lost_items) + len(found_items)
        )

    st.write("")
    st.subheader("What would you like to do?")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("🔍 Lost Something?")
            st.write(
                "Report your missing belongings "
                "and search for possible matches."
            )

            
            if st.button(
                "Report Lost Item",
                use_container_width=True,
                on_click=navigate_to,
                args=("Report Lost",)
            ):
                pass

    with col2:
        with st.container(border=True):
            st.subheader("📦 Found Something?")
            st.write(
                "Help someone recover their "
                "lost belongings."
            )

            
            if st.button(
               "Report Found Item",
                use_container_width=True,
                on_click=navigate_to,
                args=("Report Found",)
):
                pass

    st.divider()

    st.subheader("How ReFind Works")

    st.info(
        "1. Report an item → "
        "2. Store its details → "
        "3. Find potential matches → "
        "4. Review the results"
    )


elif page in ["Report Lost", "Report Found"]:

    report_type = (
        "Lost" if page == "Report Lost" else "Found"
    )

    st.header(f"Report a {report_type} Item")

    with st.form("item_form", clear_on_submit=True):

        name = st.text_input("Item Name")

        category = st.selectbox(
            "Category",
            [
                "Electronics",
                "Bags",
                "Books",
                "Accessories",
                "Other"
            ]
        )

        color = st.text_input("Color")

        location = st.text_input(
            "Last Seen Location"
            if report_type == "Lost"
            else "Found Location"
        )

        description = st.text_area(
            "Item Description",
            placeholder="Describe the item in detail..."
        )
        
        image = st.file_uploader(
            "Upload an item photo (optional)",
             type=["jpg", "jpeg", "png"]
        ) 
        submitted = st.form_submit_button(
            "Submit Report"
        )
        
        
        if submitted:
            if not name.strip() or not description.strip():
                st.error(
                    "Please enter an item name and description."
                )
            else:
                # Define image_path before checking for an image
                image_path = None

                if image is not None:
                    extension = image.name.rsplit(
                        ".", 1
                    )[-1].lower()

                    filename = (
                        f"{uuid.uuid4().hex}.{extension}"
                    )

                    image_path = os.path.join(
                        "images", filename
                    )

                    with open(image_path, "wb") as file:
                        file.write(image.getbuffer())

                # Save the report whether or not it has a photo
                item_id = add_item(
                    report_type,
                    name.strip(),
                    category,
                    color.strip(),
                    location.strip(),
                    description.strip(),
                    image_path
                )

                st.success(
                    f"{report_type} item saved! "
                    f"Report ID: {item_id}"
                )

elif page == "View Reports":

    st.header("📋 Saved Item Reports")

    filter_type = st.selectbox(
        "Filter Reports",
        ["All", "Lost", "Found"]
    )

    items = get_items(
        None if filter_type == "All" else filter_type
    )

    if not items:
        st.info("No reports found.")

    else:
        st.write(f"Showing {len(items)} reports")

        for item in items:

            with st.expander(
                f"#{item['id']} | "
                f"{item['report_type']} | "
                f"{item['name']}"
            ):
                
              if item["image_path"] and os.path.isfile(item["image_path"]):
                st.image(item["image_path"], width=250)
                st.write(
                    f"**Category:** {item['category']}"
                )
                st.write(
                    f"**Color:** {item['color']}"
                )
                st.write(
                    f"**Location:** {item['location']}"
                )
                st.write(
                    f"**Description:** {item['description']}"
                )
                st.write(
                    f"**Reported at:** {item['created_at']}"
                )



elif page == "Find Matches":

    st.header("✨ Intelligent Item Matching")

    st.write(
        "Select a report to discover potential "
        "matches using NLP."
    )

    # Select the type of report to search for
    search_type = st.radio(
        "What are you searching for?",
        ["Lost", "Found"],
        horizontal=True
    )

    reports = get_items(search_type)

    if not reports:
        st.warning(
            f"No {search_type.lower()} reports available."
        )

    else:
        report_options = {
            f"#{item['id']} - {item['name']}": item
            for item in reports
        }

        selected_label = st.selectbox(
            "Select your report",
            list(report_options.keys())
        )

        selected_item = report_options[selected_label]

        st.subheader("Selected Report")
        st.write(
            f"**Description:** "
            f"{selected_item['description']}"
        )
        st.write(
            f"**Location:** {selected_item['location']}"
        )

        if st.button(
            "🔍 Find Potential Matches",
            type="primary"
        ):

            opposite_type = (
                "Found" if search_type == "Lost"
                else "Lost"
            )

            candidates = get_items(opposite_type)

            if not candidates:
                st.info(
                    f"No {opposite_type.lower()} "
                    "reports available yet."
                )

            else:
                results = calculate_matches(
                    selected_item,
                    candidates
                )

                # Minimum similarity threshold
                results = [
                    result for result in results
                    if result["score"] >= 25
                ]

                if not results:
                    st.warning(
                        "No potential matches found."
                    )

                else:
                    st.success(
                        f"{len(results)} potential "
                        "match(es) found!"
                    )

                    for result in results:

                        item = result["item"]
                        score = result["score"]

                        with st.container(border=True):

                            st.subheader(item["name"])
                            
                            if item["image_path"] and os.path.isfile(item["image_path"]):
                                st.image(item["image_path"], width=250)

                            st.progress(
                                min(score / 100, 1)
                            )

                            st.metric(
                                "Similarity Score",
                                f"{score:.1f}%"
                            )

                            st.write(
                                f"**Category:** "
                                f"{item['category']}"
                            )

                            st.write(
                                f"**Color:** {item['color']}"
                            )

                            st.write(
                                f"**Location:** "
                                f"{item['location']}"
                            )

                            st.write(
                                f"**Description:** "
                                f"{item['description']}"
                            )

                            with st.expander(
                                "Why did this item match?"
                            ):

                                st.write(
                                    "Description similarity: "
                                    f"{result['text_similarity']}%"
                                )

                                st.write(
                                    "Category match:",
                                    result["category_match"]
                                )

                                st.write(
                                    "Color match:",
                                    result["color_match"]
                                )

                                st.write(
                                    "Location match:",
                                    result["location_match"]
                                )

                            st.caption(
                                "This is a potential match, "
                                "not a verified ownership claim."
                            )