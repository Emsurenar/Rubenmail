import os
import markdown
from anthropic import Anthropic
from dotenv import load_dotenv
from main import generate_content

def main():
    print("Testing email generation by hitting Anthropic API...")
    load_dotenv()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        return

    client = Anthropic(api_key=api_key)
    
    topics_to_test = ["Spelteori", "Formella system", "Datavetenskap"]
    
    template_path = os.path.join(os.path.dirname(__file__), "email_template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    for i, topic in enumerate(topics_to_test):
        print(f"Generating example {i+1} for topic: {topic}...")
        
        # Generate real content
        markdown_content = generate_content(client, topic, history=[])
        
        html_body = markdown.markdown(markdown_content)
        final_html = template.replace("{{content}}", html_body)
        
        test_output_path = os.path.join(os.path.dirname(__file__), f"test_email_{topic.lower().replace(' ', '_')}.html")
        with open(test_output_path, "w", encoding="utf-8") as f:
            f.write(final_html)
            
        print(f"Example saved to {test_output_path}")

if __name__ == "__main__":
    main()
