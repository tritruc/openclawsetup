#!/usr/bin/env python3
from camoufox.sync_api import Camoufox

with Camoufox(headless=True) as browser:
    page = browser.new_page()
    page.goto('https://www.facebook.com/', wait_until='domcontentloaded', timeout=60000)
    print('title:', page.title())
