from groq import Groq
from db.supabase import get_supabase
import resend

from config import get_env, get_groq_model


DIGEST_PROMPT = '''
You are a senior product manager writing a weekly feedback briefing.
Write a 200-word narrative digest for the following themes.
Write it as if you're briefing your engineering team on Monday morning.
Be specific. Include what users are asking for, what is hurting them,
and suggest one action item per major theme.

Themes this week:
{themes_json}
'''


def get_groq_client():
    return Groq(api_key=get_env('GROQ_API_KEY', required=True))


async def send_weekly_digests():
    resend.api_key = get_env('RESEND_API_KEY', required=True)
    supabase = get_supabase()
    workspaces = supabase.table('workspaces').select('*').execute().data
    for ws in workspaces:
        themes = supabase.table('themes') \
                     .select('*') \
                     .eq('workspace_id', ws['id']) \
                     .execute().data
        if not themes:
            continue

        import json
        prompt = DIGEST_PROMPT.replace('{themes_json}', json.dumps(themes, indent=2))
        resp = get_groq_client().chat.completions.create(
            model=get_groq_model(),
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=600
        )
        narrative = resp.choices[0].message.content

        # Send email via Resend
        resend.Emails.send({
            'from': 'digest@feedbackos.com',
            'to': [ws['owner_email']],
            'subject': f'Your FeedbackOS weekly digest — {ws["name"]}',
            'text': narrative
        })
