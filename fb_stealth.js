const { chromium } = require('playwright');

(async () => {
  console.log('Starting browser with stealth options...');
  
  const browser = await chromium.launch({ 
    headless: false,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage'
    ]
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1280, height: 720 }
  });
  
  const page = await context.newPage();

  // Block automation detection
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', { get: () => false });
  });

  console.log('Going to Facebook...');
  await page.goto('https://www.facebook.com', { timeout: 30000 });
  
  await page.waitForTimeout(2000);

  // Credentials loaded from environment variables (FB_EMAIL, FB_PASS)
  const fbEmail = process.env.FB_EMAIL || '';
  const fbPass = process.env.FB_PASS || '';

  // Check for login form
  const input = await page.$('input[name="email"]');
  if (input) {
    if (!fbEmail || !fbPass) {
      console.log('ERROR: FB_EMAIL or FB_PASS environment variable not set. Cannot login.');
      await browser.close();
      process.exit(1);
    }
    console.log('Found login form, filling...');
    await page.fill('input[name="email"]', fbEmail);
    await page.fill('input[name="pass"]', fbPass);
    await page.waitForTimeout(500);
    
    console.log('Clicking login...');
    await page.click('button[name="login"]').catch(async (e) => {
      console.log('Click failed, trying Enter key:', e.message);
      await page.keyboard.press('Enter');
    });
    
    console.log('Waiting for navigation...');
    await page.waitForTimeout(10000);
  }

  console.log('Current URL:', page.url());
  await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_state.png' });

  const cookies = await context.cookies();
  const cUser = cookies.find(c => c.name === 'c_user');
  console.log('c_user:', cUser ? cUser.value : 'NOT FOUND');

  if (cUser && !page.url().includes('checkpoint')) {
    console.log('\n=== LOGGED IN ===');
    
    await page.goto('https://www.facebook.com/marketplace/messages', { timeout: 15000 });
    await page.waitForTimeout(5000);
    await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_messages.png' });
    
    const bodyText = await page.textContent('body');
    
    const condoRegex = /condo[^<]{0,400}/gi;
    const matches = bodyText.match(condoRegex);
    
    if (matches && matches.length > 0) {
      console.log('\n=== CONDO MENTIONS FOUND ===');
      matches.forEach((m, i) => console.log(`${i+1}. ${m.substring(0, 400)}`));
    } else {
      console.log('\nNo condo mentions');
      console.log('First 1500 chars:', bodyText.substring(0, 1500));
    }
  } else {
    console.log('\nNot logged in or on checkpoint');
  }

  await browser.close();
  console.log('\nDone');
})();