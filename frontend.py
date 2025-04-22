# frontend.py
import gradio as gr
import webbrowser
from threading import Timer
from backend import query_database, ask_groq

def handle_query(query):
    if not query:
        return "אנא הזן שאלה."

    result = f"שאלת: {query}\n"
    result += "-" * 70 + "\n"

    chunks = query_database(query)
    context = "\n".join(chunks)

    prompt = (
        f"בהתבסס על הקונטקסט הבא, ענה על השאלה בעברית:\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )
    answer = ask_groq(prompt)

    result += "\nתשובת הבינה המלאכותית:\n"
    result += "-" * 50 + "\n"
    result += answer + "\n"
    result += "=" * 70 + "\n"

    return result

def run_gui():
    interface = gr.Interface(
        fn=handle_query,
        inputs=gr.Textbox(placeholder="הכנס שאלה כאן...", label="שאלה"),
        outputs=gr.Textbox(label="תוצאה", lines=20),
        title="MAS Project - Smart Search",
        description="שאל שאלות על מסמכים וקבל תשובות מונחות הקשר מבוססות בינה מלאכותית.",
        theme="default",
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

    app_url = interface.launch(share=False, inbrowser=False)
    print(f"Web interface is running at: {app_url}")

    def open_browser():
        webbrowser.open(app_url)
        print(f"Browser opened to: {app_url}")

    Timer(1.5, open_browser).start()
    return app_url

if __name__ == "__main__":
    run_gui()
