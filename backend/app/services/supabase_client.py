import os

class SupabaseConfig:
    URL = os.getenv("SUPABASE_URL", "https://wehwepjchdclhwsaxadg.supabase.co")
    ANON_KEY = os.getenv("SUPABASE_KEY")
    SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

    @classmethod
    def get_auth_headers(cls, use_service_role=False):
        key = cls.SERVICE_ROLE_KEY if use_service_role else cls.ANON_KEY
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }
