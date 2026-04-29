from groq import Groq
from db.supabase import supabase
import json, os
from config import get_groq_model

groq = Groq(api_key=os.getenv('GROQ_API_KEY'))

CLUSTER_PROMPT = '''
You are a product analyst. Given the following customer feedback, identify the top
5-7 recurring themes. For each theme return:
- name: short label (3-5 words)
- summary: one sentence explaining the theme
- sentiment: positive | negative | neutral
- count: approximate number of feedback items in this theme

Return ONLY valid JSON array. No explanation. No markdown.
Format: [{"name": ..., "summary": ..., "sentiment": ..., "count": ...}]

Feedback:
{feedback_text}
'''

async def detect_themes(workspace_id: str) -> list[dict]:
    # Sample up to 60 items from this workspace
    rows = supabase.table('feedback') \
               .select('raw_text') \
               .eq('workspace_id', workspace_id) \
               .limit(60).execute().data

    combined = '\n---\n'.join(r['raw_text'] for r in rows)
    prompt = CLUSTER_PROMPT.replace('{feedback_text}', combined)

    response = groq.chat.completions.create(
        model=get_groq_model(),
        messages=[{'role': 'user', 'content': prompt}],
        max_tokens=1000
    )
    themes = json.loads(response.choices[0].message.content)

    # Store themes in Supabase
    supabase.table('themes').delete().eq('workspace_id', workspace_id).execute()
    for t in themes:
        supabase.table('themes').insert({**t, 'workspace_id': workspace_id}).execute()
    return themes
