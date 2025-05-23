import os
from dotenv import load_dotenv
import PyPDF2
from bs4 import BeautifulSoup
import requests
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except FileNotFoundError:
        return "שגיאה: קובץ PDF לא נמצא."
    except Exception as e:
        return f"שגיאה בעיבוד PDF: {e}"
    return text if text else "לא נמצא טקסט בקובץ PDF."

def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        text_parts = soup.find_all('p')
        text = '\n'.join([part.get_text(strip=True) for part in text_parts])
        return text
    except requests.exceptions.RequestException as e:
        return f"שגיאה בהבאת URL: {e}"
    except Exception as e:
        return f"שגיאה בעיבוד דף אינטרנט: {e}"

def summarize_text_with_openai(text, summary_length="קצר", max_tokens=150):
    prompt = f"תמצת את הטקסט הבא בצורה {summary_length}:\n\n{text}"
    try:
        response = openai.Completion.create(
            model="text-davinci-003",  # מדויק יותר מ-gpt-3.5-turbo-instruct
            prompt=prompt,
            max_tokens=max_tokens,
            n=1,
            temperature=0.7,
        )
        if response.choices:
            return response.choices[0].text.strip()
        else:
            return "לא הצלחתי ליצור סיכום."
    except Exception as e:
        return f"שגיאה בשירות OpenAI: {e}"

def main():
    source_type = input("הזן 'file' כדי להעלות קובץ או 'url' עבור כתובת אינטרנט: ").strip().lower()

    if source_type == 'file':
        file_path = input("הזן את נתיב הקובץ (PDF או TXT): ").strip()
        if file_path.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except FileNotFoundError:
                text = "שגיאה: קובץ TXT לא נמצא."
            except Exception as e:
                text = f"שגיאה בקריאת קובץ TXT: {e}"
        else:
            text = "שגיאה: פורמט קובץ לא נתמך. אנא בחר PDF או TXT."
    elif source_type == 'url':
        url = input("הזן את כתובת האינטרנט (URL): ").strip()
        text = extract_text_from_url(url)
    else:
        print("קלט לא חוקי.")
        return

    if text and not text.startswith("שגיאה"):
        print("\nטקסט שחולץ:")
        print(text[:500] + "..." if len(text) > 500 else text)
        summary_length = input("הזן את אורך הסיכום הרצוי (קצר/בינוני/מפורט): ").strip().lower()
        if summary_length == "קצר":
            max_tokens = 150
        elif summary_length == "בינוני":
            max_tokens = 300
        elif summary_length == "מפורט":
            max_tokens = 500
        else:
            print("אורך סיכום לא חוקי, ברירת מחדל היא קצר.")
            max_tokens = 150

        summary = summarize_text_with_openai(text, summary_length=summary_length, max_tokens=max_tokens)
        print("\nסיכום:")
        print(summary)
    else:
        print(text)

if __name__ == "__main__":
    main()
