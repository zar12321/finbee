from fastapi import FastAPI
from fastapi import Request

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="app/templates"
)

@app.get("/")
def login_page(request: Request):

    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request
        }
    )