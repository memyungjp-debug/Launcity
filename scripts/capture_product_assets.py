"""Generate actual product imagery for the landing page; not fixture data or test screenshots."""
import asyncio
import base64
import sys
from pathlib import Path
from dotenv import dotenv_values
from playwright.async_api import async_playwright

async def capture():
    url=dotenv_values('/app/frontend/.env')['REACT_APP_BACKEND_URL']
    output=Path('/app/frontend/public/previews')
    output.mkdir(parents=True,exist_ok=True)
    captures={}
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,args=['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--disable-dev-shm-usage'])
        page=await browser.new_page(viewport={'width':1920,'height':800},device_scale_factor=1)
        await page.goto(f'{url}/world',wait_until='domcontentloaded',timeout=90000)
        await page.wait_for_selector('[data-testid="token-building-fartcoin"]',timeout=90000)
        await page.wait_for_timeout(2500)
        image=await page.locator('[data-testid="city-canvas"]').evaluate("canvas => canvas.toDataURL('image/jpeg', 0.9)")
        captures['world-scene.jpg']=base64.b64decode(image.split(',')[1])
        captures['world-preview.jpg']=await page.screenshot(type='jpeg',quality=20,full_page=False)
        if '--world-only' not in sys.argv:
            await page.goto(f'{url}/token/fartcoin',wait_until='domcontentloaded',timeout=60000)
            await page.wait_for_selector('[data-testid="join-community"]',timeout=45000)
            await page.wait_for_timeout(15000)
            captures['token-preview.jpg']=await page.screenshot(type='jpeg',quality=20,full_page=False)
            await page.goto(f'{url}/launch',wait_until='domcontentloaded',timeout=60000)
            await page.wait_for_selector('[data-testid="launch-name"]',timeout=45000)
            await page.wait_for_timeout(1000)
            captures['launch-preview.jpg']=await page.screenshot(type='jpeg',quality=20,full_page=False)
        await browser.close()
    # Save after browser work to avoid hot-reload navigation races during capture.
    for name,content in captures.items():(output/name).write_bytes(content)
    print('Saved authentic NEXUS product previews:',', '.join(captures))

asyncio.run(capture())