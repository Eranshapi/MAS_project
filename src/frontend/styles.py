CSS_STYLES = """
    /* ===== GLOBAL VARIABLES ===== */
    /* These variables control the main colors and dimensions used throughout the interface */
    :root {
        --background-color: #1a1f2e;  /* Main background color */
        --secondary-bg: #2a3142;      /* Secondary background color for elements */
        --text-color: #ffffff;        /* Main text color */
        --border-color: #3a4a6b;      /* Color for borders and separators */
        --accent-color: #4a6b9c;      /* Accent color for highlights and focus states */
        --header-height: 80px;        /* Height of the header section */
        --input-height: 50px;         /* Height of the input box */
        --chat-height: calc(100vh - var(--header-height) - 40px);  /* Height of chat area */
    }

    /* ===== MAIN CONTAINER STYLES ===== */
    /* Controls the overall container and background of the application */
    .gradio-container {
        background: var(--background-color) !important;
        color: var(--text-color) !important;
        height: 100vh !important;
        overflow: hidden !important;
    }

    /* ===== MAIN LAYOUT CONTAINER ===== */
    /* The main wrapper that contains all elements */
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
        position: relative !important;
    }

    /* ===== HEADER SECTION ===== */
    /* Controls the top header area with logos and title */
    .header-row {
        height: var(--header-height) !important;
        margin-bottom: 10px !important;
        display: flex !important;
        position: relative !important;
        z-index: 10 !important;
        justify-content: center !important;
    }

    /* ===== HEADER LOGOS ===== */
    /* Styling for the logo images in the header */
    .header-row img {
        pointer-events: none !important;
        user-select: none !important;
        -webkit-user-drag: none !important;
        opacity: 0.9 !important;
        filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.3)) !important;
        mix-blend-mode: luminosity !important;
        position: absolute !important;
    }

    /* Position the left logo */
    .header-row img:first-child {
        left: 20px !important;
    }

    /* Position the right logo */
    .header-row img:last-child {
        right: 20px !important;
    }

    /* ===== HEADER TEXT ===== */
    /* Styling for the main title in the header */
    .header-text {
        text-align: center !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    .header-text h1 {
        font-size: 2.5em !important;
        margin: 0 !important;
        padding: 0 !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3) !important;
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

    /* Description row */
    .description-row {
        margin-bottom: 10px !important;
        z-index: 10 !important;
        position: relative !important;
        text-align: center !important;
    }

    .description-text {
        font-size: 1.1em !important;
        color: var(--text-color) !important;
        opacity: 0.9 !important;
    }

    /* ===== INPUT AREA ===== */
    /* Controls the floating input box at the bottom */
    .chat-row {
        flex: 1 !important;
        min-height: 0 !important;
        margin: 10px 20px var(--input-height) 20px !important;
        position: relative !important;
        z-index: 1 !important;
        border-radius: 15px !important;
        max-width: 80% !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }

    .chatbot {
        background-color: var(--secondary-bg) !important;
        border: 2px solid var(--border-color) !important;
        border-radius: 20px !important;
        padding: 15px !important;
        height: calc(var(--chat-height) - 40px) !important;
        overflow-y: auto !important;
        font-size: 1em !important;
        line-height: 1.4 !important;
        box-sizing: border-box !important;
    }

    /* ===== TEXT INPUT BOX ===== */
    /* Styling for the main text input field */
    .input-row {
        position: fixed !important;
        bottom: 70px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 60% !important;  
        max-width: 600px !important; 
        height: var(--input-height) !important;
        z-index: 100 !important;
        background: var(--secondary-bg) !important;
        padding: 8px 20px !important;
        border-radius: 30px !important;
        box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.1) !important;
        display: flex !important;
        gap: 180px !important;
        align-items: center !important;
        flex-direction: row-reverse !important;
    }

    /* ===== TEXT INPUT FIELD ===== */
    /* Styling for the actual input field */
    .input-row > div,
    .input-row > div > div,
    .input-row > div > div > div,
    .gradio-input,
    .gradio-input:focus,
    .gradio-input:hover,
    .gradio-input:active,
    input.gradio-input,
    input.gradio-input:focus,
    input.gradio-input:hover,
    input.gradio-input:active,
    .input-row textarea,
    .input-row textarea:focus,
    .input-row textarea:hover,
    .input-row textarea:active {
        border: 0 !important;
        border-width: 0 !important;
        border-style: none !important;
        border-color: transparent !important;
        border-radius: 30px !important;
        padding: 0 !important;
        font-size: 1.1em !important;
        background-color: transparent !important;
        color: var(--text-color) !important;
        box-shadow: none !important;
        transition: all 0.3s ease !important;
        height: 100% !important;
        flex: 1 !important;
        outline: none !important;
        -webkit-appearance: none !important;
        -moz-appearance: none !important;
        appearance: none !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        direction: rtl !important;
        text-align: right !important;
        unicode-bidi: bidi-override !important;
    }

    /* Remove any default browser styles */
    .gradio-input::-webkit-inner-spin-button,
    .gradio-input::-webkit-outer-spin-button,
    .gradio-input::-webkit-search-decoration,
    .gradio-input::-webkit-search-cancel-button,
    .gradio-input::-webkit-search-results-button,
    .gradio-input::-webkit-search-results-decoration,
    .input-row textarea::-webkit-inner-spin-button,
    .input-row textarea::-webkit-outer-spin-button,
    .input-row textarea::-webkit-search-decoration,
    .input-row textarea::-webkit-search-cancel-button,
    .input-row textarea::-webkit-search-results-button,
    .input-row textarea::-webkit-search-results-decoration {
        -webkit-appearance: none !important;
        margin: 0 !important;
    }

    /* Override any Gradio container styles */
    .input-row > div,
    .input-row > div > div,
    .input-row > div > div > div {
        border: none !important;
        background: none !important;
        box-shadow: none !important;
    }

    /* ===== SEND BUTTON ===== */
    /* Styling for the send button */
    .input-row button,
    .input-row .gradio-button,
    .input-row button.gradio-button,
    .input-row .gradio-button.primary,
    .input-row button > div,
    .input-row .gradio-button > div,
    .input-row button.gradio-button > div,
    .input-row .gradio-button.primary > div {
        all: unset !important;
        background-color: #4a8bc0 !important;
        color: white !important;
        border: none !important;
        border-radius: 50% !important;
        width: 35px !important;
        height: 35px !important;
        min-width: 35px !important;
        max-width: 35px !important;
        min-height: 35px !important;
        max-height: 35px !important;
        padding: 0 !important;
        margin: -10px 0 auto 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2) !important;
        position: relative !important;
        overflow: hidden !important;
        line-height: 1 !important;
        box-sizing: border-box !important;
        transform: none !important;
        order: 1 !important;
        align-self: center !important;
    }

    .input-row button:hover,
    .input-row .gradio-button:hover,
    .input-row button.gradio-button:hover,
    .input-row .gradio-button.primary:hover,
    .input-row button > div:hover,
    .input-row .gradio-button > div:hover,
    .input-row button.gradio-button > div:hover,
    .input-row .gradio-button.primary > div:hover {
        background-color: #3d7aa8 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3) !important;
    }

    .input-row button *,
    .input-row .gradio-button *,
    .input-row button.gradio-button *,
    .input-row .gradio-button.primary *,
    .input-row button > div *,
    .input-row .gradio-button > div *,
    .input-row button.gradio-button > div *,
    .input-row .gradio-button.primary > div * {
        all: unset !important;
        color: white !important;
        background: transparent !important;
        display: inline-block !important;
        line-height: 1 !important;
        vertical-align: middle !important;
    }

    /* Force circular shape on all button elements */
    .input-row button,
    .input-row .gradio-button,
    .input-row button.gradio-button,
    .input-row .gradio-button.primary,
    .input-row button > div,
    .input-row .gradio-button > div,
    .input-row button.gradio-button > div,
    .input-row .gradio-button.primary > div,
    .input-row button *,
    .input-row .gradio-button *,
    .input-row button.gradio-button *,
    .input-row .gradio-button.primary *,
    .input-row button > div *,
    .input-row .gradio-button > div *,
    .input-row button.gradio-button > div *,
    .input-row .gradio-button.primary > div * {
        border-radius: 50% !important;
    }

    /* ===== CHAT MESSAGES ===== */
    /* Styling for individual chat messages */
    .chatbot .message {
        background-color: var(--border-color) !important;
        border-radius: 8px !important;
        padding: 12px !important;
        margin: 4px 0 !important;
        color: var(--text-color) !important;
        font-size: 1em !important;
        line-height: 1.3 !important;
        max-width: 85% !important;
        white-space: pre-wrap !important;
    }

    /* User message styling */
    .chatbot .user-message {
        background-color: #2c3e50 !important;
        margin-left: auto !important;
    }

    /* Bot message styling */
    .chatbot .bot-message {
        margin-right: auto !important;
    }

    /* ===== LABELS ===== */
    /* Styling for form labels */
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

    /* ===== CUSTOM SCROLLBAR ===== */
    /* Styling for the chat area scrollbar */
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

    /* ===== RESPONSIVE DESIGN ===== */
    /* Adjustments for different screen sizes */
    @media (min-width: 1024px) {
        :root {
            --header-height: 100px;
            --input-height: 60px;
        }
    }

    @media (max-width: 1023px) {
        :root {
            --header-height: 80px;
            --input-height: 60px;
        }
    }
""" 