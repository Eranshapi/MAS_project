import gradio as gr
import webbrowser
from threading import Timer
from src.backend.database import db
from src.backend.groq_client import groq_client
from src.frontend.styles import CSS_STYLES

def format_response(query, answer, chunks):
    """Format the response in a more readable way."""
    result = f"שאלת: {query}\n"
    result += "=" * 50 + "\n\n"
    
    result += "תשובת הבינה המלאכותית:\n"
    result += "-" * 40 + "\n"
    result += answer + "\n\n"
    
    result += "מקורות מידע:\n"
    result += "-" * 40 + "\n"
    for i, chunk in enumerate(chunks, 1):
        result += f"[{i}] {chunk}\n\n"
    
    result += "=" * 50 + "\n"
    return result

def handle_query(query, history):
    if not query:
        return "אנא הזן שאלה.", history
    
    # Get relevant chunks from the database
    chunks = db.query(query)
    context = "\n".join(chunks)

    # Prepare the prompt
    prompt = (
        f"תבסס על הקונטקסט הבא, ענה על השאלה בעברית:\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )
    
    # Get AI response
    answer = groq_client.ask(prompt)
    
    # Format the response
    formatted_response = format_response(query, answer, chunks)
    
    # Update history with new message format
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": formatted_response})
    
    return "", history

def create_header():
    """Create a header component with logos and title."""
    with gr.Row(elem_classes="header-row"):
        with gr.Column(scale=1, min_width=150):
            gr.Image("data/Technology_Headquarters_Logo.png", show_label=False, height=75)
        with gr.Column(scale=2):
            gr.Markdown(
                """
                # מערכת חיפוש חכמה - חיל האוויר
                ## Smart Search System - Israeli Air Force
                """,
                elem_classes="header-text"
            )
        with gr.Column(scale=1, min_width=150):
            gr.Image("data/IAF_New_Logo_2018.png", show_label=False, height=75)

def run_gui():
    """Run the enhanced GUI interface."""
    with gr.Blocks(
        css=CSS_STYLES,
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="blue",
            neutral_hue="slate",
            font=["Segoe UI", "Arial", "sans-serif"],
            radius_size="md",
            text_size="md",
            spacing_size="md",
            background_fill_primary="#1a1f2e",
            background_fill_secondary="#2a3142",
            text_color="#ffffff",
            block_background_fill="#1a1f2e",
            block_border_color="#3a4a6b",
            block_title_text_color="#ffffff",
            block_label_text_color="#ffffff",
            input_background_fill="#2a3142",
            input_border_color="#3a4a6b",
            input_text_color="#ffffff",
            button_primary_background_fill="#4a6b9c",
            button_primary_text_color="#ffffff",
            button_secondary_background_fill="#2a3142",
            button_secondary_text_color="#ffffff"
        )
    ) as interface:
        with gr.Column(elem_classes="contain"):
            create_header()
            
            with gr.Row(elem_classes="description-row"):
                with gr.Column():
                    gr.Markdown(
                        """
                        ### שאל שאלות על מסמכים וקבל תשובות מונחות הקשר מבוססות בינה מלאכותית
                        Ask questions about documents and get context-based AI-powered answers
                        """,
                        elem_classes="description-text"
                    )
            
            with gr.Row(elem_classes="input-row"):
                with gr.Column(scale=5):
                    query_input = gr.Textbox(
                        placeholder="הכנס שאלה כאן... (Enter לשליחה, Shift+Enter לשורה חדשה)",
                        label="שאלה",
                        lines=2,
                        elem_classes="query-input",
                        show_copy_button=False,
                        interactive=True,
                        autofocus=True,
                        max_lines=2
                    )
                with gr.Column(scale=1, min_width=120):
                    submit_btn = gr.Button(
                        "שלח שאלה",
                        variant="primary",
                        elem_classes="submit-button"
                    )
            
            with gr.Row(elem_classes="chat-row"):
                with gr.Column():
                    chatbot = gr.Chatbot(
                        label="תוצאות",
                        elem_classes="chatbot",
                        show_copy_button=True,
                        height=800,
                        bubble_full_width=False,
                        type="messages"  # Use the new message format
                    )
            
            # Set up event handlers
            submit_btn.click(
                handle_query,
                inputs=[query_input, chatbot],
                outputs=[query_input, chatbot]
            )
            
            query_input.submit(
                handle_query,
                inputs=[query_input, chatbot],
                outputs=[query_input, chatbot]
            )

    # Launch the interface
    app_url = interface.launch(
        share=False,
        inbrowser=False
    )
    print(f"Web interface is running at: {app_url}")

    def open_browser():
        webbrowser.open(app_url)
        print(f"Browser opened to: {app_url}")

    Timer(1.5, open_browser).start()
    return app_url 