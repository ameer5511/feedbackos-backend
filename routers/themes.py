from fastapi import APIRouter, HTTPException, Query
from db.supabase import get_themes

router = APIRouter(prefix='/themes', tags=['themes'])


@router.get('')
async def list_themes(workspace_id: str = Query(...)):
    """Get all themes for a workspace."""
    themes = await get_themes(workspace_id)
    if themes is None:
        raise HTTPException(404, 'Workspace not found')
    return {'themes': themes}


@router.get('/{workspace_id}', include_in_schema=False)
async def list_themes_by_path(workspace_id: str):
    """Backwards-compatible alias for older clients."""
    return await list_themes(workspace_id)
