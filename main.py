from fastapi import APIRouter, FastAPI
from fastapi.responses import RedirectResponse, Response
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from routers import ingest, themes, chat
from services.emailer import send_weekly_digests

app = FastAPI(title='FeedbackOS API')
scheduler = AsyncIOScheduler()


def include_api_router(router: APIRouter, name: str):
    if not isinstance(router, APIRouter):
        raise RuntimeError(f'{name} router must be a fastapi.APIRouter instance')
    app.include_router(router, prefix='/api')


include_api_router(ingest.router, 'ingest')
include_api_router(themes.router, 'themes')
include_api_router(chat.router, 'chat')

@app.on_event('startup')
async def startup():
    # Run digest every Monday at 2:30 UTC (8:00 AM IST)
    scheduler.add_job(send_weekly_digests, 'cron',
                      day_of_week='mon', hour=2, minute=30)
    scheduler.start()

@app.get('/health')
async def health():
    return {'status': 'ok'}


@app.get('/', include_in_schema=False)
async def root():
    return RedirectResponse(url='/docs')


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return Response(status_code=204)
