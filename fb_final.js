const { chromium } = require('playwright');

(async () => {
  console.log('Starting browser...');
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('Going to Facebook...');
  await page.goto('https://www.facebook.com', { timeout: 30000 });
  
  await page.waitForTimeout(2000);

  // Try to log in
  const input = await page.$('input[name="email"]');
  if (input) {
    console.log('Filling credentials...');
    await page.fill('input[name="email"]', '2152848650');
    await page.fill('input[name="pass"]', 'Conquerer4891');
    await page.waitForTimeout(500);
    
    // Click using JavaScript instead of click()
    console.log('Clicking login via JS...');
    await page.evaluate(() => {
      const btn = document.querySelector('button[name="login"]');
      if (btn) btn.click();
    });
    
    console.log('Waiting for redirect...');
    await page.waitForURL('**', { timeout: 8000 }).catch(() => {});
    await page.waitForTimeout(5000);
  }

  console.log('Current URL:', page.url());
  await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_state.png' });

  // Check if we're on two-step verification (reCAPTCHA page)
  if (page.url().includes('two_step') || page.url().includes('authentication')) {
    console.log('\n=== ON TWO-STEP/RECAPTCHA PAGE ===');
    
    // Try to find and click the reCAPTCHA checkbox
    try {
      // Method 1: Try clicking the label/checkbox inside the iframe
      console.log('Looking for reCAPTCHA checkbox...');
      const frame = page.frameLocator('iframe[title="reCAPTCHA"]').first();
      if (frame) {
        console.log('Found reCAPTCHA frame');
        const checkbox = frame.locator('#recaptcha-anchor');
        if (await checkbox.isVisible({ timeout: 3000 })) {
          console.log('Clicking reCAPTCHA checkbox...');
          await checkbox.click();
          await page.waitForTimeout(2000);
          await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_after_captcha.png' });
        }
      }
    } catch(e) {
      console.log('Method 1 failed:', e.message);
    }
    
    // Method 2: Try evaluating JavaScript to click
    try {
      console.log('Trying JS click on reCAPTCHA...');
      await page.evaluate(() => {
        const iframe = document.querySelector('iframe[src*="recaptcha"]');
        if (iframe && iframe.contentDocument) {
          const cb = iframe.contentDocument.querySelector('#recaptcha-anchor');
          if (cb) cb.click();
        }
      });
      await page.waitForTimeout(2000);
    } catch(e) {
      console.log('Method 2 failed:', e.message);
    }
    
    await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_captcha_state.png' });
    
    // Try to click the "Continue" or "Done" button after captcha
    console.log('Looking for continue button...');
    try {
      const continueBtn = page.locator('button:has-text("Continue"), button:has-text("Done"), button[type="submit"]');
      if (await continueBtn.isVisible({ timeout: 3000 })) {
        console.log('Clicking continue...');
        await continueBtn.click();
        await page.waitForTimeout(3000);
      }
    } catch(e) {
      console.log('No continue button found');
    }
    
    await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_after_cont.png' });
  }

  console.log('\nFinal URL:', page.url());
  
  // Get cookies
  const cookies = await page.context().cookies();
  const cUser = cookies.find(c => c.name === 'c_user');
  console.log('c_user cookie:', cUser ? cUser.value : 'NOT FOUND');

  if (cUser) {
    console.log('\n=== LOGGED IN ===');
    
    // Navigate to marketplace messages
    await page.goto('https://www.facebook.com/marketplace/messages', { timeout: 15000 });
    await page.waitForTimeout(5000);
    await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_messages.png' });
    
    const bodyText = await page.textContent('body');
    console.log('Messages page text length:', bodyText.length);
    
    // Search for condo
    const condoRegex = /condo[^<]{0,400}/gi;
    const matches = bodyText.match(condoRegex);
    
    if (matches && matches.length > 0) {
      console.log('\n=== CONDO MENTIONS FOUND ===');
      matches.forEach((m, i) => console.log(`${i+1}. ${m.substring(0, 400)}`));
    } else {
      console.log('\nNo condo mentions found');
      console.log('First 2000 chars:', bodyText.substring(0, 2000));
    }
  } else {
    console.log('\nNot logged in');
    // Print page text to debug
    const text = await page.textContent('body');
    console.log('Page text (first 1000):', text.substring(0, 1000));
  }

  await browser.close();
  console.log('\nDone');
})();