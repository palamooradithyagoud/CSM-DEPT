/**
 * Supabase Client Configuration
 * Uses environment variables configured in frontend/.env
 */

export const SUPABASE_CONFIG = {
  url: import.meta.env.VITE_SUPABASE_URL || 'https://wehwepjchdclhwsaxadg.supabase.co',
  anonKey: import.meta.env.VITE_SUPABASE_ANON_KEY || '',
  publishableKey: import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || '',
};

export const getSupabaseHeaders = () => ({
  apikey: SUPABASE_CONFIG.anonKey,
  Authorization: `Bearer ${SUPABASE_CONFIG.anonKey}`,
  'Content-Type': 'application/json',
});
