from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from src.core.config import app_settings


router = APIRouter()


@router.get('/', description='Redirect to doc page', include_in_schema=False)
async def root_handler():
    return RedirectResponse(app_settings.docs_url)
