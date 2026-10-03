#!/usr/bin/env python3
"""Enriquece os usernames de raw.psv com o Actor apify/instagram-profile-scraper.
Uso: APIFY_TOKEN=... python3 apify_profiles.py   -> grava apify_profiles.jsonl
Só lê dados de perfis públicos; perfis privados retornam apenas os campos públicos."""
import json, os, sys, urllib.request
TOKEN = os.environ.get("APIFY_TOKEN") or sys.exit("defina APIFY_TOKEN")
URL = ("https://api.apify.com/v2/acts/apify~instagram-profile-scraper/"
       f"run-sync-get-dataset-items?token={TOKEN}")
users = sorted({l.split('|')[0].strip().lstrip('@').lower() for l in open('raw.psv', encoding='utf-8') if '|' in l})
done = set()
if os.path.exists('apify_profiles.jsonl'):
    done = {json.loads(l).get('username', '').lower() for l in open('apify_profiles.jsonl', encoding='utf-8')}
todo = [u for u in users if u not in done]
with open('apify_profiles.jsonl', 'a', encoding='utf-8') as out:
    for i in range(0, len(todo), 50):
        body = json.dumps({"usernames": todo[i:i+50]}).encode()
        req = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
        for item in json.load(urllib.request.urlopen(req, timeout=600)):
            keep = {k: item.get(k) for k in ("username", "fullName", "biography", "externalUrl",
                    "businessCategoryName", "businessEmail", "businessPhoneNumber",
                    "businessAddressJson", "private", "verified", "followersCount")}
            out.write(json.dumps(keep, ensure_ascii=False) + "\n")
        print(f"{min(i+50, len(todo))}/{len(todo)}")
