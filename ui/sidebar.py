"""
sidebar.py — Sidebar components for the Streamlit UI.
"""

import os
import tempfile
import streamlit as st

def render_sidebar(db, get_vectorstore, ingest_pdf, reset_agents, reset_rag):
    with st.sidebar:
        # LLM Provider Switcher
        st.markdown("### ⚙️ LLM Provider")
        current_provider = os.environ.get("LLM_PROVIDER", "gemini").lower()
        
        # Display current provider badge
        if current_provider == "lmstudio":
            model_name = os.environ.get("LM_STUDIO_MODEL", "Local Model")
            st.markdown(f'<div class="provider-badge provider-lmstudio">🟢 {model_name}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="provider-badge provider-gemini">🔵 Gemini 3.0</div>', unsafe_allow_html=True)
            
        provider_options = ["gemini", "lmstudio"]
        selected_provider = st.selectbox(
            "Select Provider",
            options=provider_options,
            index=provider_options.index(current_provider),
            help="Switch between Google Gemini (Cloud) and LM Studio (Local). Switching will reset agents."
        )
        
        if selected_provider != current_provider:
            os.environ["LLM_PROVIDER"] = selected_provider
            reset_agents()
            reset_rag()
            import gc
            gc.collect()
            st.rerun()

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        
        st.markdown("### 📊 Database Stats")
        # Run a quick query to get some stats
        try:
            cust_count = db.run("SELECT COUNT(*) FROM customers")
            ticket_count = db.run("SELECT COUNT(*) FROM support_tickets")
            open_tickets = db.run("SELECT COUNT(*) FROM support_tickets WHERE status != 'Closed'")
            prod_count = db.run("SELECT COUNT(*) FROM products")
            
            # Clean up the output (SQLDatabase returns string representation of tuples)
            cust_count = cust_count.strip("[](),'")
            ticket_count = ticket_count.strip("[](),'")
            open_tickets = open_tickets.strip("[](),'")
            prod_count = prod_count.strip("[](),'")
            
            st.markdown(f"""
            <div class="stat-container">
                <div class="stat-card">
                    <div class="stat-value">{cust_count}</div>
                    <div class="stat-label">Customers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{open_tickets}</div>
                    <div class="stat-label">Open Tickets</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{ticket_count}</div>
                    <div class="stat-label">Total Tickets</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{prod_count}</div>
                    <div class="stat-label">Products</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Could not load stats: {str(e)}")

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        st.markdown("### 📚 Knowledge Base")
        try:
            vs = get_vectorstore()
            chunk_count = vs._collection.count()
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-value">{chunk_count}</div>
                <div class="stat-label">Document Chunks</div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            st.info("Knowledge base not initialized yet.")

        # PDF Upload
        st.markdown("#### 📄 Upload Policy Documents")
        uploaded_file = st.file_uploader(
            "Upload a PDF document",
            type=["pdf"],
            help="Upload company policy PDFs to build the knowledge base",
        )
        if uploaded_file is not None:
            # Create a unique key for the file so we only ingest it once per session
            if "ingested_files" not in st.session_state:
                st.session_state.ingested_files = set()
                
            file_key = f"{uploaded_file.name}_{uploaded_file.size}"
            
            if file_key not in st.session_state.ingested_files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                with st.spinner(f"📥 Indexing {uploaded_file.name}..."):
                    try:
                        count = ingest_pdf(tmp_path)
                        st.session_state.ingested_files.add(file_key)
                        st.success(f"✅ Indexed {count} chunks from {uploaded_file.name}")
                        os.unlink(tmp_path)
                        # Refresh to update the Knowledge Base stats in the sidebar
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        # Quick Actions
        st.markdown("#### ⚡ Quick Actions")
        
        if st.button("👤 Ema's Profile"):
            st.session_state.pending_query = "Show me the profile for Ema"
            st.rerun()
            
        if st.button("🔄 Refund Policy"):
            st.session_state.pending_query = "What is the standard refund policy?"
            st.rerun()
            
        if st.button("📊 Open Tickets"):
            st.session_state.pending_query = "Show me all open support tickets"
            st.rerun()
            
        if st.button("🏷️ Premium Customers"):
            st.session_state.pending_query = "Who are our Premium plan customers?"
            st.rerun()
            
        if st.button("🔒 Privacy Policy"):
            st.session_state.pending_query = "How do we handle customer data according to the privacy policy?"
            st.rerun()

        if st.button("🎫 Escalated Issues"):
            st.session_state.pending_query = "What are the current escalated tickets and their resolution notes?"
            st.rerun()

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
        
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        # Seed policies
        if st.button("📥 Load Sample Policies", key="seed_policies"):
            with st.spinner("Creating and indexing sample policy documents..."):
                try:
                    from create_sample_policy import create_sample_policies
                    create_sample_policies()
                    from agents.rag_agent import ingest_all_policies
                    count = ingest_all_policies()
                    st.success(f"✅ Indexed {count} chunks from sample policies")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        # Clear & Rebuild KB (needed after switching providers with different embedding dims)
        if st.button("🔄 Clear & Rebuild KB", key="rebuild_kb"):
            with st.spinner("Clearing old knowledge base and rebuilding..."):
                try:
                    import gc
                    import shutil

                    chroma_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "chroma_db")

                    # Step 1: Fully release ChromaDB file handles (closes SQLite connections)
                    reset_rag()
                    gc.collect()

                    # Step 2: Remove the physical directory to ensure a clean slate
                    if os.path.exists(chroma_dir):
                        shutil.rmtree(chroma_dir)

                    # Step 3: Re-ingest sample policies with the current provider's embeddings
                    from create_sample_policy import create_sample_policy_text
                    from langchain_core.documents import Document
                    from langchain_text_splitters import RecursiveCharacterTextSplitter

                    policy_text = create_sample_policy_text()
                    doc = Document(page_content=policy_text, metadata={"source_file": "acme_company_policies.pdf", "page": 0})

                    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                    splits = splitter.split_documents([doc])

                    vs = get_vectorstore()
                    vs.add_documents(splits)
                    st.success(f"✅ Knowledge base rebuilt with {len(splits)} chunks using current provider")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error rebuilding KB: {str(e)}")
