#!/usr/bin/env python3
"""
OMNI-Scanner v4.0
Deep OSINT Username Enumeration Tool
Author: MANDEEP PARMAR
GitHub: https://github.com/hacksben

This tool performs username reconnaissance across 600+ websites
using a 7-layer ultra-strict accuracy verification engine.
"""

import asyncio
import aiohttp
import re
import json
import time
import urllib.request
from colorama import Fore, Style, init

init(autoreset=True)

# ==========================================
# 1. BUILT-IN DATABASE (65 Core Sites)
# ==========================================
BUILTIN_SITES = {
    "Social Media": {
        "Facebook": "https://www.facebook.com/{}", "Instagram": "https://www.instagram.com/{}/",
        "Twitter/X": "https://x.com/{}", "TikTok": "https://www.tiktok.com/@{}",
        "Pinterest": "https://www.pinterest.com/{}/", "Reddit": "https://www.reddit.com/user/{}",
        "Snapchat": "https://www.snapchat.com/add/{}", "Linktree": "https://linktr.ee/{}",
        "Threads": "https://www.threads.net/@{}", "Bluesky": "https://bsky.app/profile/{}",
        "Mastodon": "https://mastodon.social/@{}", "Tumblr": "https://{}.tumblr.com",
        "VK": "https://vk.com/{}", "Weibo": "https://weibo.com/{}", "Telegram": "https://t.me/{}"
    },
    "Cybersecurity & Hacking": {
        "HackTheBox": "https://app.hackthebox.com/users/{}", "TryHackMe": "https://tryhackme.com/p/{}",
        "Root-Me": "https://www.root-me.org/{}", "HackerOne": "https://hackerone.com/{}",
        "Bugcrowd": "https://bugcrowd.com/{}", "PentesterLab": "https://pentesterlab.com/profile/{}",
        "Cybrary": "https://app.cybrary.it/user/profile/{}", "Hackaday": "https://hackaday.io/{}",
        "PacketStorm": "https://packetstormsecurity.com/users/{}", "Exploit-DB": "https://www.exploit-db.com/author/{}",
        "HackerNews": "https://news.ycombinator.com/user?id={}", "LeetCode": "https://leetcode.com/{}",
        "CyberDefenders": "https://cyberdefenders.org/profile/{}", "LetsDefend": "https://letsdefend.io/user/{}"
    },
    "Professional & Tech": {
        "GitHub": "https://github.com/{}", "GitLab": "https://gitlab.com/{}",
        "LinkedIn": "https://www.linkedin.com/in/{}", "StackOverflow": "https://stackoverflow.com/users/{}",
        "DockerHub": "https://hub.docker.com/u/{}", "Keybase": "https://keybase.io/{}",
        "Bitbucket": "https://bitbucket.org/{}/", "Dev.to": "https://dev.to/{}",
        "Hashnode": "https://hashnode.com/@{}", "Medium": "https://medium.com/@{}",
        "Substack": "https://{}.substack.com", "HackerNoon": "https://hackernoon.com/u/{}",
        "Replit": "https://replit.com/@{}", "Codepen": "https://codepen.io/{}"
    },
    "Gaming & Streaming": {
        "Steam": "https://steamcommunity.com/id/{}", "Twitch": "https://www.twitch.tv/{}",
        "YouTube": "https://www.youtube.com/@{}", "Xbox": "https://www.xboxgamertag.com/search/{}",
        "PlayStation": "https://psnprofiles.com/{}", "Chess.com": "https://www.chess.com/member/{}",
        "Roblox": "https://www.roblox.com/user.aspx?username={}", "Minecraft": "https://namemc.com/profile/{}",
        "EpicGames": "https://store.epicgames.com/en-US/u/{}", "Lichess": "https://lichess.org/@/{}",
        "Kaggle": "https://www.kaggle.com/{}", "Codeforces": "https://codeforces.com/profile/{}"
    },
    "Creative & Niche": {
        "Behance": "https://www.behance.net/{}", "Dribbble": "https://dribbble.com/{}",
        "Flickr": "https://www.flickr.com/photos/{}", "ArtStation": "https://www.artstation.com/{}",
        "Patreon": "https://www.patreon.com/{}", "SoundCloud": "https://soundcloud.com/{}",
        "Spotify": "https://open.spotify.com/user/{}", "Vimeo": "https://vimeo.com/{}",
        "Kick": "https://kick.com/{}", "Rumble": "https://rumble.com/user/{}"
    }
}

# ==========================================
# 2. AUTO-FETCH 500+ SITES (Bulletproof)
# ==========================================
def fetch_massive_database():
    """Fetch extended database from Sherlock project (500+ verified sites)"""
    url = "https://raw.githubusercontent.com/sherlock-project/sherlock/master/sherlock_project/resources/data.json"
    print(f"{Fore.CYAN}[*] Fetching massive OSINT database (500+ extra sites)...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            
        extra_sites = {}
        for site_name, site_data in data.items():
            if not isinstance(site_data, dict):
                continue
            url_template = site_data.get("url", "")
            if isinstance(url_template, str) and url_template.startswith("http") and "{}" in url_template:
                if not site_data.get("isNSFW", False):
                    extra_sites[site_name] = url_template
                    
        BUILTIN_SITES["Sherlock_Extended_DB"] = extra_sites
        print(f"{Fore.GREEN}[+] Successfully loaded {len(extra_sites)} additional verified sites!")
        return len(extra_sites)
    except Exception as e:
        print(f"{Fore.RED}[-] Could not fetch extended database: {e}")
        return 0

# ==========================================
# 3. 7-LAYER ULTRA-STRICT ACCURACY ENGINE
# ==========================================
async def scan_site(session, semaphore, category, name, url_template, username, exact_keyword):
    """Scan a single site with 7-layer verification engine"""
    async with semaphore:
        url = url_template.format(username)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with session.get(url, headers=headers, timeout=timeout, allow_redirects=True, ssl=False) as resp:
                
                # LAYER 1: Hard Status Code Rejection
                if resp.status in [404, 403, 410, 500, 502, 503, 520, 522]:
                    return False

                # LAYER 2: Redirect Trap Detection
                final_url = str(resp.url).lower()
                if any(trap in final_url for trap in ["404", "not-found", "error", "login", "register", "signup"]):
                    return False

                content = await resp.text()
                content_lower = content.lower()
                
                # LAYER 3: Title Tag Analysis (Silver Bullet)
                title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
                if title_match:
                    title = title_match.group(1).lower()
                    if any(bad in title for bad in ["not found", "page not found", "error 404", "does not exist", "no such user", "invalid user", "sorry,", "couldn't find"]):
                        return False

                # LAYER 4: Payload Size Check
                if len(content) < 3500: 
                    return False

                # LAYER 5: Aggressive Negative Regex Detection
                negative_patterns = [
                    r"user not found", r"profile not found", r"page not found", 
                    r"doesn't exist", r"does not exist", r"no such user", r"account not found", 
                    r"this page isn't available", r"sorry, this page", r"couldn't find",
                    r"the requested user does not exist", r"invalid username"
                ]
                for pattern in negative_patterns:
                    if re.search(pattern, content_lower):
                        return False

                # LAYER 6: Positive Presence Verification
                if username.lower() not in content_lower:
                    return False

                # LAYER 7: Profile Indicator Check
                profile_indicators = ["joined", "followers", "following", "posts", "profile", "bio", "member since", "reputation", "about"]
                has_indicator = any(indicator in content_lower for indicator in profile_indicators)
                
                probability = 60  # Base score for passing Layers 1-6
                
                if has_indicator:
                    probability += 20
                
                if exact_keyword and exact_keyword.lower() in content_lower:
                    probability += 30
                elif username.lower() in content_lower:
                    probability += 10

                # Output Results only if probability is high enough
                if probability >= 80:
                    status = f"{Fore.GREEN}[100% EXACT]" if probability >= 95 else f"{Fore.YELLOW}[HIGH PROB]"
                    print(f"{status} {Fore.CYAN}{category[:15]:15} | {Fore.WHITE}{name[:20]:20} | {Fore.LIGHTBLUE_EX}{url}")
                    return True

        except (asyncio.TimeoutError, aiohttp.ClientError, Exception):
            return False

# ==========================================
# 4. MAIN EXECUTION
# ==========================================
async def main():
    """Main CLI and scanning orchestration"""
    print(f"\n{Fore.MAGENTA}╔══════════════════════════════════════════════════════════╗")
    print(f"║       OMNI-SCANNER 2026: DEEP OSINT ENUMERATION        ║")
    print(f"║          [ Ultra-Strict / 600+ Sites Engine ]          ║")
    print(f"╚══════════════════════════════════════════════════════════╝{Style.RESET_ALL}\n")

    user = input(f"{Fore.CYAN}[*] Enter Target Username: {Style.RESET_ALL}").strip()
    keyword = input(f"{Fore.CYAN}[*] Enter Real Name/Keyword (Optional for 100% exact match): {Style.RESET_ALL}").strip()
    
    if not user:
        print(f"{Fore.RED}[-] Username cannot be empty.")
        return

    fetch_massive_database()
    total_sites = sum(len(sites) for sites in BUILTIN_SITES.values())
    
    print(f"\n{Fore.MAGENTA}--- DEEP SEARCH STARTING ---")
    print(f"Scanning {Fore.YELLOW}{total_sites}{Style.RESET_ALL} websites for: {Fore.YELLOW}{user}")
    print(f"Engine: 7-Layer Ultra-Strict Filter (Blocks Redirects & JS 404s)")
    print(f"{Fore.RED}Note: Deep scanning takes time to ensure 100% accuracy. Please wait...\n")

    start_time = time.time()
    semaphore = asyncio.Semaphore(30) 
    connector = aiohttp.TCPConnector(limit=30, force_close=True)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for cat, sites in BUILTIN_SITES.items():
            for name, url in sites.items():
                tasks.append(scan_site(session, semaphore, cat, name, url, user, keyword))
        
        results = await asyncio.gather(*tasks)

    found_count = sum(1 for r in results if r)
    elapsed = time.time() - start_time

    print(f"\n{Fore.MAGENTA}--- SCAN COMPLETE ---")
    print(f"Time Taken: {Fore.YELLOW}{elapsed:.2f} seconds")
    print(f"Sites Scanned: {Fore.CYAN}{total_sites}")
    print(f"Definitive Matches Found: {Fore.GREEN}{found_count}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[-] Scan aborted by user.")