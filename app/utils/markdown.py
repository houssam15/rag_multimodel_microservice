import markdown
from bs4 import BeautifulSoup

def strip_markdown(md_text: str) -> str:
    """
    Converts markdown to plain text.
    """
    html = markdown.markdown(md_text)
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")