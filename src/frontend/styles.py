CSS_STYLES = """
    /* Global styles */
    :root {
        --background-color: #1a1f2e;
        --secondary-bg: #2a3142;
        --text-color: #ffffff;
        --border-color: #3a4a6b;
        --accent-color: #4a6b9c;
        --header-height: 80px;
        --input-height: 100px;
        --chat-height: calc(100vh - var(--header-height) - var(--input-height) - 80px);
    }

    /* Override Gradio's default styles */
    .gradio-container {
        background: var(--background-color) !important;
        color: var(--text-color) !important;
        height: 100vh !important;
        overflow: hidden !important;
    }

    /* Main container styling */
    .contain {
        font-family: 'Segoe UI', 'Arial', sans-serif !important;
        font-size: 16px !important;
        width: 100% !important;
        height: 100vh !important;
        margin: 0 !important;
        padding: 20px !important;
        background: linear-gradient(to bottom, var(--background-color), var(--secondary-bg)) !important;
        color: var(--text-color) !important;
        display: flex !important;
        flex-direction: column !important;
        overflow: hidden !important;
    }

    /* Header styling */
    .header-row {
        height: var(--header-height) !important;
        margin-bottom: 10px !important;
        display: flex !important;
        align-items: center !important;
        position: relative !important;
    }

    /* Logo styling */
    .header-row img {
        pointer-events: none !important;
        user-select: none !important;
        -webkit-user-drag: none !important;
        opacity: 0.9 !important;
        filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3)) !important;
        mix-blend-mode: luminosity !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color) !important;
        margin: 0 !important;
    }

    #title {
        text-align: center !important;
        color: var(--text-color) !important;
        font-size: 2em !important;
        font-weight: bold !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3) !important;
    }

    #description {
        text-align: center !important;
        color: var(--text-color) !important;
        font-size: 1.1em !important;
        margin-bottom: 10px !important;
        line-height: 1.4 !important;
    }

    /* Input area styling */
    .input-row {
        height: var(--input-height) !important;
        margin-bottom: 10px !important;
        display: flex !important;
        align-items: center !important;
    }

    .gradio-input {
        border: 2px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 1.1em !important;
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
        transition: all 0.3s ease !important;
        height: 100% !important;
    }

    .gradio-input:focus {
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 8px rgba(74, 107, 156, 0.4) !important;
    }

    /* Button styling */
    .gradio-button {
        background: linear-gradient(to bottom, #2c3e50, #34495e) !important;
        color: var(--text-color) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-size: 1.1em !important;
        font-weight: bold !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
        height: 100% !important;
    }

    .gradio-button:hover {
        background: linear-gradient(to bottom, #34495e, #2c3e50) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
    }

    /* Chat area styling */
    .chat-row {
        flex: 1 !important;
        min-height: 0 !important;
        margin-bottom: 0 !important;
    }

    .chatbot {
        background-color: var(--secondary-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 20px !important;
        height: var(--chat-height) !important;
        overflow-y: auto !important;
        font-size: 1.2em !important;
        line-height: 1.6 !important;
    }

    .chatbot .message {
        background-color: var(--border-color) !important;
        border-radius: 8px !important;
        padding: 15px !important;
        margin: 8px 0 !important;
        color: var(--text-color) !important;
        font-size: 1.2em !important;
        line-height: 1.6 !important;
        max-width: 85% !important;
    }

    .chatbot .user-message {
        background-color: #2c3e50 !important;
        margin-left: auto !important;
    }

    .chatbot .bot-message {
        margin-right: auto !important;
    }

    /* Label styling */
    .gradio-label {
        font-weight: bold !important;
        color: var(--text-color) !important;
        font-size: 1.1em !important;
        margin-bottom: 4px !important;
    }

    /* Markdown styling */
    .markdown {
        color: var(--text-color) !important;
    }

    .markdown h1 {
        color: var(--text-color) !important;
        font-size: 1.8em !important;
        margin-bottom: 8px !important;
    }

    .markdown h2 {
        color: var(--text-color) !important;
        font-size: 1.4em !important;
        margin-bottom: 6px !important;
    }

    .markdown h3 {
        color: var(--text-color) !important;
        font-size: 1.2em !important;
        margin-bottom: 4px !important;
    }

    /* Description row */
    .description-row {
        margin-bottom: 10px !important;
    }

    /* Responsive adjustments */
    @media (min-width: 1024px) {
        :root {
            --header-height: 100px;
            --input-height: 120px;
        }
    }

    @media (max-width: 1023px) {
        :root {
            --header-height: 80px;
            --input-height: 100px;
        }
    }

    /* Custom scrollbar for chat area */
    .chatbot::-webkit-scrollbar {
        width: 8px !important;
    }

    .chatbot::-webkit-scrollbar-track {
        background: var(--secondary-bg) !important;
        border-radius: 4px !important;
    }

    .chatbot::-webkit-scrollbar-thumb {
        background: var(--border-color) !important;
        border-radius: 4px !important;
    }

    .chatbot::-webkit-scrollbar-thumb:hover {
        background: var(--accent-color) !important;
    }
""" 