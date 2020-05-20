import typing
import uuid
import aioredis
from fastapi import FastAPI, Depends, Request, Form
from fastapi_plugins import depends_redis, redis_plugin, RedisSettings
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


class AppSettings(RedisSettings):
    api_name: str = str(__name__)


app = FastAPI()
config = AppSettings()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{key}")
async def get_key(request: Request, key, db: aioredis.Redis = Depends(depends_redis)):
    note = await db.get(key)
    if note:
        await db.delete(key)
        return templates.TemplateResponse("result.html", {"request": request,
                                                          "note": note.decode("utf-8")})
    else:
        return templates.TemplateResponse("deleted.html", {"request": request})


@app.post("/created")
async def created(request: Request, note: str = Form(...), db: aioredis.Redis = Depends(depends_redis)):
    key = str(uuid.uuid4())
    await db.set(key, note)

    return templates.TemplateResponse("generated_link.html", {"request": request,
                                                              "key": key})


@app.on_event('startup')
async def on_startup() -> None:
    await redis_plugin.init_app(app, config=config)
    await redis_plugin.init()


@app.on_event('shutdown')
async def on_shutdown() -> None:
    await redis_plugin.terminate()
