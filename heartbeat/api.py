from contextlib import asynccontextmanager

from fastapi import APIRouter
from heartbeat.service import service

router = APIRouter(prefix='/heartbeat')


@asynccontextmanager
async def lifespan(app):
    service.start()
    try:
        yield
    finally:
        service.close()


@router.get('/status')
def status():
    return {'text': service.status()}


@router.post('/stop')
def stop():
    service.stop()
    return {'text': 'Heartbeat stop requested; automatic checks paused.'}


@router.post('/resume')
def resume():
    return {'text': service.resume()}
