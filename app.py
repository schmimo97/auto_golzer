import streamlit as st
import requests
from langchain.callbacks import get_openai_callback

from langchain.chat_models import ChatOpenAI
from bs4 import BeautifulSoup
import requests
from langchain.schema import (
    SystemMessage,
    HumanMessage,
)

def get_article(url: str) -> str:
    "Get Raw article text from url."
    response = requests.get(url)

    if response.status_code != 200:
        response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    
    for selector in ['div.a-u-inline', 'footer.beitragsfooter', 'a-opt-in']: #List elements to drop
        for element in soup.select(selector):
            element.decompose()

    article = soup.find('article', class_='akwa-article article-content')
    article_text = article.get_text(separator='\n', strip=True)
    return article_text

def summarize_and_generate_questions(summary_prompt, questions_prompt, article_text, chat):
    summary_prompt = f"{summary_prompt}:\n\n{article_text}"
    questions_prompt = f"{questions_prompt}:\n\n{article_text}"
    with get_openai_callback() as cb:

        messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=summary_prompt)
        ]
        summary = chat(messages)

        messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=questions_prompt)
        ]
        questions = chat(messages)

    return summary.content, questions.content, cb



if __name__ == "__main__":
    st.title("Auto-Golzer")

    with st.sidebar:
        api_key = st.text_input("Enter your OpenAI API Key:", type="password")
        default_summary_prompt = "Fasse den Inhalt des Textes in wenigen literarisch anspruchsvollen Sätzen zusammen, achte auf eine starke Wortwahl.\n\n"
        default_question_prompt = """Erzeuge 3 Fragen über den Artikel, die zur Diskussion anregen. Sprich die Leser immer direkt mit "Sie" an. \nHier sind gute Beispiele:\n\nWie bewerten Sie die möglichen Konsequenzen eines weiteren Absikens der Rentenniveaus?\n Wie sollte das Geld ihrer Meinung nach eingesetzt werden?\nWie schätzen Sie die Erfolgsaussichten des geplanten Vorstoßes zur Sicherung des Roten Meeres ein? \nRede das Publikum immer direkt an.\n\n"""

        summary_prompt_text = st.text_area("Customize your summary prompt:", value=default_summary_prompt)
        questions_prompt_text = st.text_area("Customize your questions prompt:", value=default_question_prompt)
        model = st.radio("Choose an AI model:", ('gpt-4-1106-preview', 'gpt-3.5-turbo-1106'))


    url = st.text_input("Enter the URL of the article:")
    if st.button("Generate Summary and Questions"):
        if url and api_key:
            chat = ChatOpenAI(
                openai_api_key=api_key,
                temperature=0,
                model=model
            )
            article_text = get_article(url)

            if article_text:
                summary, questions, cb = summarize_and_generate_questions(summary_prompt_text, questions_prompt_text, article_text, chat)

                st.subheader("Facebook Post")
                st.write(summary)
                st.subheader("Questions")
                st.write(questions)
                st.write(cb)

            else:
                st.error("Unable to retrieve article content. Please check the URL.")
        else:
            st.error("Please provide both a URL and an OpenAI API Key.")

