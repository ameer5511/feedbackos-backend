from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.rag import answer_from_feedback

router = APIRouter(prefix='/chat', tags=['chat'])


class ChatRequest(BaseModel):
    question: str
    workspace_id: str


@router.post('')
async def chat(req: ChatRequest):
    """Ask a question about feedback in a workspace."""
    try:
        result = await answer_from_feedback(req.question, req.workspace_id)
        return {
            'answer': result['answer'],
            'sources': result['sources']
        }
    except Exception as e:
        raise HTTPException(500, str(e))
