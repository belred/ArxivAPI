import asyncio
import textwrap

from fastapi import APIRouter, Request, Form
from bs4 import BeautifulSoup
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from translate import Translator

from model import Article
from requests import get

arxiv_router = APIRouter()
templates = Jinja2Templates(directory="templates/")

@arxiv_router.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@arxiv_router.get("/search/id")
async def search_by_id(request: Request):
    return templates.TemplateResponse("search_by_id.html", {"request": request})

@arxiv_router.post("/search/id")
async def search_by_id(request: Request, arxiv_id: str = Form(...)):
    return RedirectResponse(url=f"/search/{arxiv_id}", status_code=303)

@arxiv_router.get("/search")
async def search_articles(request: Request, query: str = ""):
    if not query:
        return templates.TemplateResponse("arxiv.html", {"request": request})

    base_url = "https://arxiv.org/search/cs?"
    params = {
        "query": query,
        "searchtype": "title",
        "abstracts": "show",
        "order": "-announced_date_first"
    }
    response = get(base_url, params=params)
    html_content = response.text
    article = parse_arxiv(html_content)

    return templates.TemplateResponse("arxiv.html", {
        "request": request,
        "articles": article,
        "query": query
    })

def parse_arxiv(html_content: str):
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = []
    for result in soup.find_all('li', class_='arxiv-result'):
        id_link = result.find('p', class_='list-title').find('a')['href']
        arxiv_id = id_link.split('/')[-1]  #извлекаем часть после последнего /
        title = result.find('p', class_='title is-5 mathjax').text.strip()
        authors = [a.text.strip() for a in result.find_all('a', href=lambda x: x and 'author' in x)]
        abstract = result.find('p', class_='abstract mathjax').text.replace('Abstract:', '').strip()

        article = Article(
            id=arxiv_id,
            title=title,
            authors=authors,
            abstract=abstract
        )
        articles.append(article)

    return articles

@arxiv_router.get("/search/{arxiv_id}")
async def get_article_by_id(request: Request, arxiv_id: str):
    base_url = f"https://arxiv.org/abs/{arxiv_id}"
    response = get(base_url)
    html_content = response.text
    article = parse_single_article(html_content, arxiv_id)

    return templates.TemplateResponse("article_detail.html", {
        "request": request,
        "article": article
    })

def parse_single_article(html_content: str, arxiv_id: str):
    soup = BeautifulSoup(html_content, 'html.parser')
    title = soup.find('h1', class_='title mathjax').text.replace('Title:', '').strip()
    authors = [a.text.strip() for a in soup.find_all('a', href=lambda x: x and 'author' in x)]
    abstract = soup.find('blockquote', class_='abstract mathjax').text.replace('Abstract:', '').strip()

    return Article(
        id=arxiv_id,
        title=title,
        authors=authors,
        abstract=abstract,
    )

@arxiv_router.get("/search/{arxiv_id}/translate")
async def show_translated_article(request: Request, arxiv_id: str):
    try:
        base_url = f"https://arxiv.org/abs/{arxiv_id}"
        response = get(base_url)
        html_content = response.text
        article = parse_single_article(html_content, arxiv_id)

        translator = Translator(to_lang="ru")

        chunks = textwrap.wrap(article.abstract, width=500, replace_whitespace=False)
        translated_chunks = []

        for chunk in chunks:
            translated = translator.translate(chunk)
            translated_chunks.append(translated)
            await asyncio.sleep(0.5)

        full_translation = " ".join(translated_chunks)

        return templates.TemplateResponse("article_translate.html", {
            "request": request,
            "article": article,
            "translated_text": full_translation
        })

    except Exception as e:
        base_url = f"https://arxiv.org/abs/{arxiv_id}"
        response = get(base_url)
        html_content = response.text
        article = parse_single_article(html_content, arxiv_id)

        return templates.TemplateResponse("article_translate.html", {
            "request": request,
            "article": article,
            "error": f"Translation error: {str(e)}"
        }, status_code=500)