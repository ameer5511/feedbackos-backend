from functools import lru_cache

from supabase import create_client

from config import get_env


@lru_cache(maxsize=1)
def get_supabase():
    return create_client(
        get_env("SUPABASE_URL", required=True),
        get_env("SUPABASE_KEY", required=True),
    )


async def store_feedback(items: list):
    rows = [
        {
            "id": str(i.id),
            "workspace_id": str(i.workspace_id),
            "raw_text": i.raw_text,
            "source": i.source,
            "source_meta": i.source_meta,
            "char_count": i.char_count,
        }
        for i in items
    ]
    get_supabase().table("feedback").insert(rows).execute()


async def mark_embedded(feedback_id):
    get_supabase().table("feedback").update({"is_embedded": True}).eq(
        "id", str(feedback_id)
    ).execute()


async def get_workspace(workspace_id: str):
    result = (
        get_supabase().table("workspaces")
        .select("*")
        .eq("id", workspace_id)
        .single()
        .execute()
    )
    return result.data


async def get_themes(workspace_id: str):
    result = (
        get_supabase().table("themes")
        .select("*")
        .eq("workspace_id", workspace_id)
        .execute()
    )
    return result.data


# Alias for backward compatibility
supabase = get_supabase()
