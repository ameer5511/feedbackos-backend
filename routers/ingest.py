from fastapi import APIRouter, UploadFile, BackgroundTasks, Header, HTTPException
import pandas as pd
from models.feedback import FeedbackItem
from services.chunker import chunk_text
from services.embedder import embed_and_store
from db.supabase import store_feedback, get_workspace

router = APIRouter()

# ── SOURCE 1: Paste raw text ──────────────────────────────────────────
@router.post('/ingest/paste', status_code=202)
async def ingest_paste(payload: dict, workspace_id: str, bt: BackgroundTasks):
    chunks = chunk_text(payload['text'])
    if not chunks:
        raise HTTPException(400, 'No feedback items found. Paste text must include at least one item with 40+ characters.')
    items = [FeedbackItem(raw_text=c, source='paste', workspace_id=workspace_id)
             for c in chunks]
    await store_feedback(items)
    bt.add_task(embed_and_store, items)   # runs after response returns
    return {'status': 'processing', 'queued': len(items)}

# ── SOURCE 2: CSV upload ──────────────────────────────────────────────
@router.post('/ingest/csv', status_code=202)
async def ingest_csv(file: UploadFile, text_column: str,
                     workspace_id: str, bt: BackgroundTasks):
    df = pd.read_csv(file.file)
    if text_column not in df.columns:
        raise HTTPException(400, f'Column not found. Available: {list(df.columns)}')
    items = [FeedbackItem(raw_text=str(row[text_column]), source='csv',
                         workspace_id=workspace_id)
             for _, row in df.iterrows() if len(str(row[text_column])) > 30]
    if not items:
        raise HTTPException(400, 'No feedback items found. Check the selected text column and row length.')
    await store_feedback(items)
    bt.add_task(embed_and_store, items)
    return {'status': 'processing', 'queued': len(items)}

# ── SOURCE 3: Zapier / third-party webhook ────────────────────────────
@router.post('/ingest/webhook/{workspace_id}', status_code=202)
async def ingest_webhook(workspace_id: str, payload: dict,
                         x_feedbackos_secret: str = Header(None),
                         bt: BackgroundTasks = None):
    ws = await get_workspace(workspace_id)
    if x_feedbackos_secret != ws['webhook_secret']:
        raise HTTPException(403, 'Invalid secret')
    text = next((str(payload[k]) for k in
                 ['text','body','message','response','feedback'] if k in payload),
                str(payload))
    item = FeedbackItem(raw_text=text, source='webhook', workspace_id=workspace_id)
    await store_feedback([item])
    bt.add_task(embed_and_store, [item])
    return {'status': 'ok'}
