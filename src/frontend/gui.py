import gradio as gr
import webbrowser
import os
import base64
from threading import Timer
from src.backend.database import db
from src.backend.groq_client import groq_client
from src.frontend.styles import CSS_STYLES

# Get absolute paths for images
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TECH_LOGO_PATH = os.path.join(BASE_DIR, "data", "Technology_Headquarters_Logo.png")
IAF_LOGO_PATH = os.path.join(BASE_DIR, "data", "IAF_New_Logo_2018.png")

# Convert images to base64 for reliable display
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

TECH_LOGO_BASE64 = image_to_base64(TECH_LOGO_PATH)
IAF_LOGO_BASE64 = image_to_base64(IAF_LOGO_PATH)

def format_response(query, answer, chunks_with_scores):
    """Format the response in a more readable way."""
    result = f"שאלת: {query}\n"
    result += "=" * 50 + "\n\n"
    
    result += "תשובת הבינה המלאכותית:\n"
    result += "-" * 40 + "\n"
    result += answer + "\n\n"
    
    result += "מקורות מידע:\n"
    result += "-" * 40 + "\n"
    for i, (chunk, score) in enumerate(chunks_with_scores, 1):
        result += f"[{i}] (דמיון: {score:.2%})\n{chunk}\n\n"
    
    result += "=" * 50 + "\n"
    return result

def handle_query(query, history):
    if not query:
        return "", history
    
    # Get relevant chunks from the database with scores
    chunks_with_scores = db.query(query, k=3, score_threshold=0.1)  # Match the database threshold
    
    # Debug logging
    print(f"\nQuery: {query}")
    print(f"Found {len(chunks_with_scores)} chunks")
    for i, (chunk, score) in enumerate(chunks_with_scores):
        print(f"Chunk {i+1} score: {score:.2%}")
    
    if not chunks_with_scores:
        return "", history
    
    # Extract just the chunks for context
    chunks = [chunk for chunk, _ in chunks_with_scores]
    context = "\n".join(chunks)

    # Prepare the prompt with enhanced structure and instructions
    prompt = (
        "אתה עוזר חכם שמטרתו לענות על שאלות בהתבסס על מידע מוסמך. "
        "השתמש במידע הבא כדי לענות על השאלה בצורה מקצועית ומדויקת:\n\n"
        f"מידע רלוונטי:\n{context}\n\n"
        f"שאלה: {query}\n\n"
        "הוראות:\n"
        "1. ענה בעברית בלבד\n"
        "2. השתמש רק במידע שסופק בקונטקסט\n"
        "3. אם המידע בקונטקסט לא מספיק, ציין זאת\n"
        "4. שמור על תשובה ברורה וממוקדת\n"
        "5. אם יש מספר נקודות חשובות, פרט אותן בנקודות"
    )
    
    # Get AI response
    answer = groq_client.ask(prompt)
    
    # Format the response
    formatted_response = format_response(query, answer, chunks_with_scores)
    
    # Update history with new message format
    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": formatted_response})
    
    return "", history

def create_header():
    """Create a header component with logos and title."""
    with gr.Row(elem_classes="header-row"):
        # Technology Headquarters Logo
        gr.HTML(
            f'<img src="data:image/png;base64,{TECH_LOGO_BASE64}" alt="Technology Headquarters Logo">',
            elem_classes="left-logo"
        )
        gr.Markdown(
            """
            # מערכת חיפוש חכמה - חיל האוויר
            """,
            elem_classes="header-text"
        )
        # IAF Logo
        gr.HTML(
            f'<img src="data:image/png;base64,{IAF_LOGO_BASE64}" alt="IAF Logo">',
            elem_classes="right-logo"
        )

def run_gui():
    """Run the enhanced GUI interface."""
    with gr.Blocks(css=CSS_STYLES) as interface:
        with gr.Column(elem_classes="contain"):
            create_header()
            
            with gr.Row(elem_classes="input-row"):
                with gr.Column(scale=5):
                    query_input = gr.Textbox(
                        show_label=False,
                        placeholder="הכנס שאלה כאן... (Enter לשליחה, Shift+Enter לשורה חדשה)",
                        label=None,
                        lines=1,
                        elem_classes="query-input",
                        show_copy_button=False,
                        interactive=True,
                        autofocus=True,
                        max_lines=1
                    )
                with gr.Column(scale=1, min_width=80):
                    submit_btn = gr.Button(
                        "שלח",
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
            
            # Handle Enter key press (Gradio's built-in submit event)
            query_input.submit(
                handle_query,
                inputs=[query_input, chatbot],
                outputs=[query_input, chatbot]
            )

    # Launch the interface
    app_url = interface.launch(
        share=False,
        inbrowser=False,
        prevent_thread_lock=True,
        show_api=False
    )
    print(app_url[1]+"?__theme=dark")
    
    def open_browser():
        webbrowser.open(app_url[1]+"?__theme=dark")
        print(f"Browser opened to: {app_url[1]}?__theme=dark")

    Timer(1.5, open_browser).start()
    
    try:
        # Keep the main thread alive
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down server...")
        interface.close()
    
    return app_url 
    