import typing
import aioredis
from fastapi import FastAPI, Depends, Request
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
async def root_get(cache: aioredis.Redis = Depends(depends_redis)):
    return dict(ping=await cache.ping())


@app.on_event('startup')
async def on_startup() -> None:
    await redis_plugin.init_app(app, config=config)
    await redis_plugin.init()


@app.on_event('shutdown')
async def on_shutdown() -> None:
    await redis_plugin.terminate()
