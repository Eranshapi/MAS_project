# frontend.py
import gradio as gr
import webbrowser
from threading import Timer
from backend import query_database, ask_groq  # Import functions from backend.py

# Gradio web interface function
def handle_query(query):
    if not query:
        return "Please enter a question."
    
    result = f"You asked: {query}\n"
    result += "-" * 70 + "\n"
    
    chunks = query_database(query)
    context = "\n".join(chunks)
    
    prompt = f"בהתבסס על הקונטקסט הבא תענה על השאלה בעברית:\n\nContext:\n{context}\n\nQuestion: {query}"
    answer = ask_groq(prompt)
    
    result += "\nGroq Answer:\n"
    result += "-" * 50 + "\n"
    result += answer + "\n"
    result += "=" * 70 + "\n"
    
    return result

# Create and launch the web interface
def run_gui():
    # Create Gradio interface
    interface = gr.Interface(
        fn=handle_query,
        inputs=gr.Textbox(placeholder="Enter your question here...", label="Question"),
        outputs=gr.Textbox(label="Results", lines=20),
        title="MAS Project - Smart Search",
        description="Ask questions about your documents and get AI-powered answers.",
        theme="huggingface",
        css="""
            .gradio-container {font-family: 'Arial', sans-serif; font-size: 16px;}
            #title {text-align: center;}
            #description {text-align: center;}
            .gradio-container::before {
                content: "";
                position: absolute;
                top: 20px;
                left: 20px;
                background-image: url('data/Technology_Headquarters_Logo.png');
                background-size: contain;
                width: 100px;
                height: 50px;
            }
            .gradio-container::after {
                content: "";
                position: absolute;
                top: 20px;
                right: 20px;
                background-image: url('data/IAF_New_Logo_2018.png');
                background-size: contain;
                width: 100px;
                height: 50px;
            }
        """
    )
    
    # Launch the interface
    app_url = interface.launch(share=False, inbrowser=False)
    print(f"Web interface is running at: {app_url}")
    
    # Open the browser after a short delay
    def open_browser():
        webbrowser.open(app_url)
        print(f"Browser opened to: {app_url}")
    
    Timer(1.5, open_browser).start()
    
    return app_url

if __name__ == "__main__":
    run_gui()
