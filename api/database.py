from supabase import create_client, Client
from typing import Optional

_supabase_client: Optional[Client] = None


def init_supabase(url: str, key: str) -> Client:
    global _supabase_client
    _supabase_client = create_client(url, key)
    return _supabase_client


def get_supabase() -> Client:
    if _supabase_client is None:
        raise RuntimeError("Supabase client not initialized. Call init_supabase first.")
    return _supabase_client
