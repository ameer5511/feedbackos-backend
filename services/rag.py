from services.embedder import embed_text
from db.supabase import get_supabase
from groq import Groq

from config import get_env, get_groq_model

RAG_PROMPT = '''
You are a product analyst. Answer the user's question using ONLY the feedback
excerpts below. Be specific and cite evidence from the feedback.
If the answer is not in the feedback, say so clearly.

Feedback excerpts:
{context}

Question: {question}
'''


def get_groq_client():
    return Groq(api_key=get_env('GROQ_API_KEY', required=True))


async def answer_from_feedback(question: str, workspace_id: str) -> dict:
    # 1. Embed the user's question
    q_vector = embed_text(question)

    # 2. Find top 5 most similar feedback items via pgvector
    result = get_supabase().rpc('match_feedback', {
        'query_embedding': q_vector,
        'workspace_id': workspace_id,
        'match_count': 5
    }).execute()

    # match_feedback is a Supabase function (see schema.sql addendum below)
    chunks = [r['raw_text'] for r in result.data]
    context = '\n---\n'.join(chunks)

    # 3. Call Groq with context + question
    prompt = RAG_PROMPT.replace('{context}', context).replace('{question}', question)
    resp = get_groq_client().chat.completions.create(
        model=get_groq_model(),
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=500
    )
    return {
        'answer': resp.choices[0].message.content,
        'sources': chunks[:3]   # return top 3 source quotes to the UI
    }

# Add this function to Supabase via SQL editor:
# create or replace function match_feedback(
#   query_embedding vector(384),
#   workspace_id uuid,
#   match_count int
# ) returns table (raw_text text, similarity float) as $$
#   select f.raw_text, 1-(e.embedding <=> query_embedding) as similarity
#   from embeddings e join feedback f on e.feedback_id = f.id
#   where f.workspace_id = match_feedback.workspace_id
#   order by e.embedding <=> query_embedding
#   limit match_count;
# $$ language sql stable;
