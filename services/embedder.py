from huggingface_hub import InferenceClient
from db.supabase import get_supabase, mark_embedded

from config import get_env

HF_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'


def get_hf_client():
    return InferenceClient(token=get_env('HF_TOKEN', required=True))


def embed_text(text: str) -> list[float]:
    result = get_hf_client().feature_extraction(text, model=HF_MODEL)
    if hasattr(result, 'tolist'):
        return result.tolist()
    return list(result)


async def embed_and_store(items: list):
    supabase = get_supabase()
    for item in items:
        try:
            vector = embed_text(item.raw_text)
            supabase.table('embeddings').insert({
                'feedback_id': str(item.id),
                'embedding': vector
            }).execute()
            await mark_embedded(item.id)
        except Exception as e:
            print(f'Embedding failed for {item.id}: {e}')
            # Fail silently — will retry on next ingestion cycle
