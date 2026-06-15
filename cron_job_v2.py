#!/usr/bin/env python3
# cron_job_v2.py - Genera cookie per i 40 nuovi account con sistema di retry

import asyncio
import os
import random
import gc
from datetime import datetime
from supabase import create_client
from browser_use_sdk import AsyncBrowserUse
from playwright.async_api import async_playwright

# ==================== CONFIGURAZIONE ====================
KEYS_SUPABASE_URL = os.environ.get("KEYS_SUPABASE_URL", "https://kdqzfsmibquvvobjvjlj.supabase.co")
KEYS_SUPABASE_KEY = os.environ.get("KEYS_SUPABASE_KEY")
COOKIE_SUPABASE_URL = os.environ.get("COOKIE_SUPABASE_URL", "https://ofijopixtpwahgbwyutc.supabase.co")
COOKIE_SUPABASE_KEY = os.environ.get("COOKIE_SUPABASE_KEY")

DEFAULT_PASSWORD = "DDnmVV45!!"
MAX_ATTEMPTS = 7
PAUSE_BETWEEN_ACCOUNTS = 15
PAUSE_BEFORE_RETRY = 30
TIMEOUT = 90000

# 40 nuovi account
ACCOUNTS = [
    {'email': 'sandrominori50+ucupamikowa@gmail.com', 'name': 'ucupamikowa'},
    {'email': 'sandrominori50+ubbmaad@gmail.com', 'name': 'ubbmaad'},
    {'email': 'sandrominori50+unachizaadaa@gmail.com', 'name': 'unachizaadaa'},
    {'email': 'sandrominori50+uzofequ@gmail.com', 'name': 'uzofequ'},
    {'email': 'sandrominori50+ugaglchimulu@gmail.com', 'name': 'ugaglchimulu'},
    {'email': 'sandrominori50+usfnejafi@gmail.com', 'name': 'usfnejafi'},
    {'email': 'sandrominori50+ugaufkokagl@gmail.com', 'name': 'ugaufkokagl'},
    {'email': 'sandrominori50+utuufvo@gmail.com', 'name': 'utuufvo'},
    {'email': 'sandrominori50+umufela@gmail.com', 'name': 'umufela'},
    {'email': 'sandrominori50+uzukimice@gmail.com', 'name': 'uzukimice'},
    {'email': 'sandrominori50+uvatulukofo@gmail.com', 'name': 'uvatulukofo'},
    {'email': 'sandrominori50+ugetrle@gmail.com', 'name': 'ugetrle'},
    {'email': 'sandrominori50+usfkugl@gmail.com', 'name': 'usfkugl'},
    {'email': 'sandrominori50+uzuculo@gmail.com', 'name': 'uzuculo'},
    {'email': 'sandrominori50+uxipgda@gmail.com', 'name': 'uxipgda'},
    {'email': 'sandrominori50+ulidazurzmu@gmail.com', 'name': 'ulidazurzmu'},
    {'email': 'sandrominori50+uncglximo@gmail.com', 'name': 'uncglximo'},
    {'email': 'sandrominori50+ufezusavo@gmail.com', 'name': 'ufezusavo'},
    {'email': 'sandrominori50+ulileaature@gmail.com', 'name': 'ulileaature'},
    {'email': 'sandrominori50+ulorenakino@gmail.com', 'name': 'ulorenakino'},
    {'email': 'sandrominori50+uqulenazusa@gmail.com', 'name': 'uqulenazusa'},
    {'email': 'sandrominori50+ukaramu@gmail.com', 'name': 'ukaramu'},
    {'email': 'sandrominori50+uferalola@gmail.com', 'name': 'uferalola'},
    {'email': 'sandrominori50+ummmarzsarm@gmail.com', 'name': 'ummmarzsarm'},
    {'email': 'sandrominori50+udatrlefe@gmail.com', 'name': 'udatrlefe'},
    {'email': 'sandrominori50+uaakiggzu@gmail.com', 'name': 'uaakiggzu'},
    {'email': 'sandrominori50+uzorzvu@gmail.com', 'name': 'uzorzvu'},
    {'email': 'sandrominori50+uwanepgbo@gmail.com', 'name': 'uwanepgbo'},
    {'email': 'sandrominori50+udioodali@gmail.com', 'name': 'udioodali'},
    {'email': 'sandrominori50+usadiadmobo@gmail.com', 'name': 'usadiadmobo'},
    {'email': 'sandrominori50+ulixire@gmail.com', 'name': 'ulixire'},
    {'email': 'sandrominori50+udiadnczo@gmail.com', 'name': 'udiadnczo'},
    {'email': 'sandrominori50+uzalesagg@gmail.com', 'name': 'uzalesagg'},
    {'email': 'sandrominori50+upabbkafone@gmail.com', 'name': 'upabbkafone'},
    {'email': 'sandrominori50+uramincadkr@gmail.com', 'name': 'uramincadkr'},
    {'email': 'sandrominori50+uganakaeara@gmail.com', 'name': 'uganakaeara'},
    {'email': 'sandrominori50+urerafokrne@gmail.com', 'name': 'urerafokrne'},
    {'email': 'sandrominori50+ufiwakota@gmail.com', 'name': 'ufiwakota'},
    {'email': 'sandrominori50+ukrfojudi@gmail.com', 'name': 'ukrfojudi'},
    {'email': 'sandrominori50+uornewafomo@gmail.com', 'name': 'uornewafomo'},
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def get_all_working_keys():
    if not KEYS_SUPABASE_KEY:
        log("❌ KEYS_SUPABASE_KEY non impostata")
        return []
    try:
        supabase = create_client(KEYS_SUPABASE_URL, KEYS_SUPABASE_KEY)
        resp = supabase.table('browser_use_keys').select('api_key').eq('status', 'working').execute()
        return [row['api_key'] for row in resp.data] if resp.data else []
    except Exception as e:
        log(f"❌ Errore recupero chiavi: {e}")
        return []

def get_random_working_key(exclude_keys=None):
    keys = get_all_working_keys()
    if not keys:
        return None
    if exclude_keys:
        keys = [k for k in keys if k not in exclude_keys]
    return random.choice(keys) if keys else None

def save_cookie_to_db(email, nome_utente, cookie_string, sesids, user_id):
    if not COOKIE_SUPABASE_KEY:
        log("❌ COOKIE_SUPABASE_KEY non impostata")
        return False
    try:
        supabase = create_client(COOKIE_SUPABASE_URL, COOKIE_SUPABASE_KEY)
        divella_format = f"{nome_utente}|{cookie_string}"
        data = {
            'email': email,
            'nome_utente': nome_utente,
            'account_name': nome_utente,
            'divella_format': divella_format,
            'cookie_string': cookie_string,
            'sesids': sesids,
            'user_id': user_id,
            'status': 'active',
            'updated_at': datetime.now().isoformat()
        }
        supabase.table('account_cookies').upsert(data, on_conflict='email').execute()
        log(f"   💾 Salvato su Supabase")
        return True
    except Exception as e:
        log(f"   ❌ Errore salvataggio: {e}")
        return False

async def generate_cookie_for_account(api_key, account, is_retry=False):
    email = account['email']
    nome = account['name']
    
    log(f"🚀 {nome} - {email}")
    log(f"   🔑 Chiave: {api_key[:20]}...")
    if is_retry:
        log(f"   🔄 TENTATIVO DI RECUPERO")
    
    client = AsyncBrowserUse(api_key=api_key)
    profile = None
    
    try:
        profile = await client.profiles.create(name=f"cookie_{nome}")
        browser = await client.browsers.create(profile_id=profile.id)
        
        async with async_playwright() as p:
            pw_browser = await p.chromium.connect_over_cdp(browser.cdp_url)
            page = pw_browser.contexts[0].pages[0]
            
            await page.goto("https://www.easyhits4u.com/logon/", timeout=TIMEOUT)
            await page.wait_for_timeout(5000)
            
            try:
                await page.wait_for_selector('input[name="cf-turnstile-response"]', timeout=30000)
                await page.wait_for_timeout(3000)
            except:
                log(f"   ⚠️ Turnstile non rilevato, procedo...")
            
            await page.fill('#username', email)
            await page.fill('#password', DEFAULT_PASSWORD)
            await page.keyboard.press('Enter')
            
            await page.wait_for_timeout(45000)
            
            cookies = await page.context.cookies()
            cookie_string = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
            sesids = next((c['value'] for c in cookies if c['name'] == 'sesids'), None)
            user_id = next((c['value'] for c in cookies if c['name'] == 'user_id'), None)
            
            if sesids and user_id:
                log(f"   ✅ OK - sesids={sesids}")
                save_cookie_to_db(email, nome, cookie_string, sesids, user_id)
                return True
            else:
                log(f"   ❌ Cookie non trovati")
                return False
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg:
            log(f"   ⚠️ RATE LIMIT (429)")
            return "rate_limit"
        else:
            log(f"   ❌ Errore: {error_msg[:80]}")
            return False
    finally:
        if profile:
            try:
                await client.profiles.delete(profile.id)
            except:
                pass
        try:
            await client.close()
        except:
            pass
        await asyncio.sleep(2)
        gc.collect()

async def main():
    log("=" * 60)
    log("CRON JOB V2 - 40 NUOVI ACCOUNT CON RETRY")
    log("=" * 60)
    
    if not KEYS_SUPABASE_KEY:
        log("❌ Variabile KEYS_SUPABASE_KEY non impostata")
        return
    
    all_keys = get_all_working_keys()
    if not all_keys:
        log("❌ Nessuna chiave working")
        return
    
    log(f"🔑 Chiavi working: {len(all_keys)}")
    
    # ==================== PRIMO CICLO ====================
    successi = 0
    falliti_list = []
    
    for i, account in enumerate(ACCOUNTS):
        log(f"\n📌 [{i+1}/{len(ACCOUNTS)}] {account['name']}")
        
        used_keys = []
        success = False
        
        for attempt in range(MAX_ATTEMPTS):
            api_key = get_random_working_key(exclude_keys=used_keys)
            if not api_key:
                break
            
            result = await generate_cookie_for_account(api_key, account, is_retry=False)
            
            if result == True:
                success = True
                successi += 1
                break
            elif result == "rate_limit":
                used_keys.append(api_key)
                log(f"   🔄 Rate limit, cambio chiave ({attempt+1}/{MAX_ATTEMPTS})...")
                continue
            else:
                # Fallimento non dovuto a rate limit
                break
        
        if not success:
            falliti_list.append(account)
            log(f"   ❌ Account fallito, verrà ritentato")
        
        if i < len(ACCOUNTS) - 1:
            await asyncio.sleep(PAUSE_BETWEEN_ACCOUNTS)
    
    log(f"\n📊 Primo ciclo completato: {successi} successi, {len(falliti_list)} falliti")
    
    # ==================== SECONDO CICLO (RITENTATIVI) ====================
    if falliti_list:
        log("\n" + "=" * 60)
        log(f"🔄 SECONDO CICLO - RITENTO {len(falliti_list)} ACCOUNT FALLITI")
        log("=" * 60)
        
        # Attendi prima di ritentare
        log(f"⏳ Attesa {PAUSE_BEFORE_RETRY} secondi prima del secondo ciclo...")
        await asyncio.sleep(PAUSE_BEFORE_RETRY)
        
        recuperati = 0
        
        for i, account in enumerate(falliti_list):
            log(f"\n📌 RITENTO [{i+1}/{len(falliti_list)}] {account['name']}")
            
            used_keys = []
            success = False
            
            for attempt in range(MAX_ATTEMPTS):
                api_key = get_random_working_key(exclude_keys=used_keys)
                if not api_key:
                    break
                
                result = await generate_cookie_for_account(api_key, account, is_retry=True)
                
                if result == True:
                    success = True
                    recuperati += 1
                    successi += 1
                    break
                elif result == "rate_limit":
                    used_keys.append(api_key)
                    log(f"   🔄 Rate limit, cambio chiave ({attempt+1}/{MAX_ATTEMPTS})...")
                    continue
                else:
                    break
            
            if success:
                log(f"   ✅ RECUPERATO!")
            else:
                log(f"   ❌ Recupero fallito")
            
            if i < len(falliti_list) - 1:
                await asyncio.sleep(PAUSE_BETWEEN_ACCOUNTS)
        
        log(f"\n📊 Recuperati nel secondo ciclo: {recuperati}/{len(falliti_list)}")
    
    # ==================== RIEPILOGO FINALE ====================
    log("\n" + "=" * 60)
    log("📊 RIEPILOGO FINALE")
    log("=" * 60)
    log(f"✅ Successi totali: {successi}")
    log(f"❌ Falliti totali: {len(ACCOUNTS) - successi}")
    log(f"📊 Totale account: {len(ACCOUNTS)}")
    log("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
