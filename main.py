import os
import json
import random
import markdown
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from email_sender import send_email

# Load environment variables
load_dotenv()

# Configuration
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'history.json')
TOPICS = [
    "AI", 
    "Spelteori", 
    "Nationalekonomi", 
    "Beteendeekonomi",
    "Datavetenskap", 
    "Marknadsföring", 
    "Formella system"
]
WORD_COUNT_TARGET = 700

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-30:], f, ensure_ascii=False, indent=2)  # Keep last 30
    except Exception as e:
        print(f"Failed to save history: {e}")

def generate_content(client, topic, history):
    system_prompt = (
        "Du är en briljant, intellektuell skribent och folkbildare. "
        "Ditt mål är att skriva en rigorösa, djupgående men tillgänglig text "
        f"på cirka {WORD_COUNT_TARGET} ord om ett specifikt koncept inom {topic}.\n\n"
        "Målgruppen är en intelligent och nyfiken läsare som dock saknar formell fackkunskap. "
        "Du får INTE 'dumma ner' materialet, men du måste förklara det pedagogiskt och elegant.\n\n"
        "Kontextualisera ämnet direkt i inledningen så att läsaren omedelbart förstår hur "
        "djupt, spännande och viktigt detta koncept är.\n\n"
        "Var rigorös, stringent, informationstät. SKRIV INGET ONÖDIGT. VAR SÅ INFROMATIONSTÄT DU KAN."
        "Formatering:\n"
        "- Använd en passande, säljande huvudrubrik (använd Markdown # för rubrik).\n"
        "- Använd underrubriker (##) för struktur.\n"
        "- VIKTIGT: Skriv endast första ordet med stor bokstav i alla rubriker, oavsett om det är huvudrubrik eller underrubrik (t.ex. 'Artificiell dumhet' istället för 'Artificiell Dumhet').\n"
        "- Inkludera gärna konkreta exempel.\n"
        "- Skriv på felfri, sofistikerad svenska.\n\n"
        "Viktigt: UNDVIK följande koncept då vi nyligen skrivit om dem:\n" + 
        "\n".join([f"- {item}" for item in history])
    )

    prompt = f"Skriv dagens insiktsfulla mail om ett spännande koncept inom {topic}. Ge mig endast själva texten i Markdown-format utan extra introduktioner."

    print(f"Generating content for topic: {topic}...")
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2500,
        temperature=0.7,
        system=system_prompt,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text

def extract_title(markdown_text):
    for line in markdown_text.split('\n'):
        if line.startswith('# '):
            return line[2:].strip()
    return "Daily dose of dark chocolate"

def main():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        return

    client = Anthropic(api_key=api_key)
    
    # Select a random topic
    topic = random.choice(TOPICS)
    
    # Load history to avoid repetition
    history = load_history()
    
    # Generate content
    markdown_content = generate_content(client, topic, history)
    
    # Extract Title to save to history
    title = extract_title(markdown_content)
    history.append(f"{topic}: {title}")
    save_history(history)
    
    # Convert markdown to HTML
    html_body = markdown.markdown(markdown_content)
    
    # Wrap in email template
    template_path = os.path.join(os.path.dirname(__file__), "email_template.html")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
    except Exception as e:
        print(f"Error reading template: {e}")
        return

    final_html = template.replace("{{content}}", html_body)
    
    # Send email
    print("Sending email...")
    send_email(final_html)

if __name__ == "__main__":
    main()
