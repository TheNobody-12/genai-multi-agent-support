"""
styles.py — Custom CSS for the Streamlit UI.
"""

def get_custom_css():
    return """
<style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ── Header ── */
    .main-header {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.12), rgba(118, 75, 162, 0.12));
        border: 1px solid rgba(102, 126, 234, 0.25);
        border-radius: 16px;
        padding: 1.25rem 1.75rem;
        margin-bottom: 1.25rem;
        backdrop-filter: blur(20px);
    }
    .main-header h1 {
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
    }
    .main-header p {
        color: var(--text-color);
        opacity: 0.75;
        margin: 0.4rem 0 0 0;
        font-size: 0.9rem;
    }

    /* ── Chat messages ── */
    [data-testid="stChatMessage"] {
        background: rgba(128, 128, 128, 0.04);
        border: 1px solid rgba(128, 128, 128, 0.08);
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        backdrop-filter: blur(10px);
        max-width: 100%;
        overflow: hidden;
    }

    /* ── CRITICAL: Responsive tables inside chat ── */
    [data-testid="stChatMessage"] table {
        display: block;
        width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        border-collapse: collapse;
        font-size: 0.85rem;
        white-space: nowrap;
    }
    [data-testid="stChatMessage"] table th,
    [data-testid="stChatMessage"] table td {
        padding: 0.5rem 0.75rem;
        border: 1px solid rgba(128, 128, 128, 0.15);
        text-align: left;
        white-space: nowrap;
    }
    [data-testid="stChatMessage"] table th {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.08));
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        position: sticky;
        top: 0;
    }
    [data-testid="stChatMessage"] table tr:nth-child(even) {
        background: rgba(128, 128, 128, 0.03);
    }
    [data-testid="stChatMessage"] table tr:hover {
        background: rgba(102, 126, 234, 0.06);
    }

    /* Also fix any dataframe/table Streamlit renders */
    [data-testid="stChatMessage"] [data-testid="stTable"],
    [data-testid="stChatMessage"] .stMarkdown {
        max-width: 100%;
        overflow-x: auto;
    }

    /* ── Markdown content inside chat ── */
    [data-testid="stChatMessage"] .stMarkdown p {
        line-height: 1.65;
        margin-bottom: 0.5rem;
    }
    [data-testid="stChatMessage"] .stMarkdown ul,
    [data-testid="stChatMessage"] .stMarkdown ol {
        padding-left: 1.25rem;
        margin-bottom: 0.5rem;
    }
    [data-testid="stChatMessage"] .stMarkdown li {
        margin-bottom: 0.25rem;
        line-height: 1.55;
    }
    [data-testid="stChatMessage"] .stMarkdown strong {
        color: var(--text-color);
        font-weight: 600;
    }
    [data-testid="stChatMessage"] .stMarkdown code {
        background: rgba(102, 126, 234, 0.08);
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
        font-size: 0.82rem;
    }

    /* ── Chat input ── */
    [data-testid="stChatInput"] {
        border-radius: 20px !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05) !important;
        background: var(--bg-color);
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #667eea !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.15) !important;
    }

    /* ── Badges ── */
    .route-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        letter-spacing: 0.02em;
    }
    .route-sql { background: rgba(56, 189, 248, 0.15); color: #0284c7; border: 1px solid rgba(56, 189, 248, 0.3); }
    .route-rag { background: rgba(52, 211, 153, 0.15); color: #059669; border: 1px solid rgba(52, 211, 153, 0.3); }
    .route-both { background: rgba(167, 139, 250, 0.15); color: #7c3aed; border: 1px solid rgba(167, 139, 250, 0.3); }

    /* Dark mode adjustments */
    @media (prefers-color-scheme: dark) {
        .route-sql { color: #38bdf8; }
        .route-rag { color: #34d399; }
        .route-both { color: #a78bfa; }
    }

    /* ── Sidebar tweaks ── */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-bg);
        border-right: 1px solid rgba(128, 128, 128, 0.1);
    }
    .sidebar-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(128, 128, 128, 0.2), transparent);
        margin: 1.5rem 0;
    }

    /* Quick action buttons */
    div.stButton > button {
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.2);
        background: rgba(128, 128, 128, 0.05);
        transition: all 0.2s ease;
        padding: 0.4rem 0.8rem;
    }
    div.stButton > button:hover {
        background: rgba(102, 126, 234, 0.1);
        border-color: rgba(102, 126, 234, 0.4);
        transform: translateY(-1px);
    }

    /* Stats container */
    .stat-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .stat-card {
        background: rgba(128, 128, 128, 0.05);
        border: 1px solid rgba(128, 128, 128, 0.1);
        border-radius: 8px;
        padding: 0.75rem 0.5rem;
        text-align: center;
        transition: transform 0.2s ease;
    }
    .stat-card:hover {
        background: rgba(128, 128, 128, 0.08);
        transform: translateY(-2px);
    }
    .stat-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.2rem;
    }
    .stat-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        opacity: 0.7;
    }
    
    /* Active Provider Badge */
    .provider-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 1rem;
        width: 100%;
        justify-content: center;
        gap: 0.5rem;
    }
    .provider-gemini {
        background: rgba(26, 115, 232, 0.15);
        color: #1a73e8;
        border: 1px solid rgba(26, 115, 232, 0.3);
    }
    .provider-lmstudio {
        background: rgba(52, 211, 153, 0.15);
        color: #059669;
        border: 1px solid rgba(52, 211, 153, 0.3);
    }
    @media (prefers-color-scheme: dark) {
        .provider-gemini { color: #8ab4f8; }
        .provider-lmstudio { color: #34d399; }
    }
</style>
"""
