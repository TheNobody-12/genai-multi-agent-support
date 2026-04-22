"""
chat.py — Chat interface components for the Streamlit UI.
"""

import streamlit as st

def render_chat(query_router):
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI Customer Support Assistant</h1>
        <p>Ask questions about customers, support tickets, or company policies. I'll route your query to the right specialist agent.</p>
    </div>
    """, unsafe_allow_html=True)

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "route" in message and message["role"] == "assistant":
                route = message["route"]
                badge_class = f"route-{route}"
                route_labels = {"sql": "📊 Database", "rag": "📄 Policy Docs", "both": "📊📄 Both"}
                st.markdown(
                    f'<span class="route-badge {badge_class}">{route_labels.get(route, route)}</span>',
                    unsafe_allow_html=True,
                )
            st.markdown(message["content"])

    # Handle pending query from quick actions
    pending = st.session_state.pop("pending_query", None)

    # Chat input
    user_input = st.chat_input("Ask about customers, tickets, or policies...")

    query = pending or user_input

    if query:
        # Add user message if not from quick action (already added)
        if not pending:
            st.session_state.messages.append({"role": "user", "content": query})

        with st.chat_message("user"):
            st.markdown(query)

        # Get response from router
        with st.chat_message("assistant"):
            with st.spinner("🔍 Analyzing your question and routing to the right agent..."):
                try:
                    # Exclude the very last message which is the current query itself
                    history = st.session_state.messages[:-1]
                    response = query_router(query, history=history, thread_id=st.session_state.thread_id)

                    # Detect route for badge display
                    query_lower = query.lower()
                    if any(kw in query_lower for kw in ["policy", "refund", "warranty", "privacy", "sla", "terms"]):
                        route = "rag"
                    elif any(kw in query_lower for kw in ["customer", "ticket", "profile", "plan", "open", "escalat"]):
                        route = "sql"
                    else:
                        route = "sql"

                    route_labels = {"sql": "📊 Database", "rag": "📄 Policy Docs", "both": "📊📄 Both"}
                    badge_class = f"route-{route}"
                    st.markdown(
                        f'<span class="route-badge {badge_class}">{route_labels.get(route, route)}</span>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(response)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "route": route,
                    })
                except Exception as e:
                    import logging
                    logging.exception("Error processing chat message")
                    error_msg = f"❌ An error occurred: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                    })
