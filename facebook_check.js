const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('Starting fresh login to Facebook...');
  
  // Go to Facebook
  await page.goto('https://www.facebook.com');
  await page.waitForTimeout(2000);
  
  // Credentials loaded from environment variables
  const fbEmail = process.env.FB_EMAIL || '';
  const fbPass = process.env.FB_PASS || '';

  // Check if we need to log in
  const emailInput = await page.$('input[name="email"]');
  if (emailInput) {
    if (!fbEmail || !fbPass) {
      console.log('ERROR: FB_EMAIL or FB_PASS environment variable not set.');
      await browser.close();
      process.exit(1);
    }
    console.log('Filling login form...');
    await page.fill('input[name="email"]', fbEmail);
    await page.fill('input[name="pass"]', fbPass);
    await page.click('button[name="login"]');
    
    // Wait for redirect after login click
    console.log('Waiting for login to process...');
    await page.waitForTimeout(8000);
    
    console.log('URL after login:', page.url());
    await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_login_attempt.png' });
  }

  // Check what page we're on now
  const currentUrl = page.url();
  
  if (currentUrl.includes('checkpoint') || currentUrl.includes('two_step') || currentUrl.includes('authentication')) {
    console.log('\n=== ON SECURITY CHECKPOINT ===');
    await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_checkpoint.png' });
    
    // Get the page content to understand what verification is needed
    const pageContent = await page.content();
    
    if (pageContent.includes('recaptcha')) {
      console.log('reCAPTCHA detected, looking for checkbox...');
      
      // Try to find and interact with reCAPTCHA
      try {
        const recaptchaFrame = page.frameLocator('iframe[src*="recaptcha"]').first();
        if (recaptchaFrame) {
          console.log('Found recaptcha frame');
          const checkbox = recaptchaFrame.locator('.recaptcha-checkbox');
          if (await checkbox.isVisible({ timeout: 3000 })) {
            console.log('Clicking reCAPTCHA checkbox...');
            await checkbox.click();
            await page.waitForTimeout(3000);
            await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_after_captcha.png' });
          }
        }
      } catch(e) {
        console.log('Could not interact with reCAPTCHA:', e.message);
      }
      
      // After captcha, try to continue
      console.log('Trying to submit after captcha...');
      await page.click('button[type="submit"], #checkpointBottomBar button', { timeout: 5000 }).catch(e => console.log('No submit button found'));
      await page.waitForTimeout(5000);
    }
    
    await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_checkpoint_after.png' });
  }

  console.log('\nFinal URL:', page.url());
  await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_final_state.png' });

  // Get cookies to confirm login state
  const cookies = await context.cookies();
  console.log('\nCookies after login attempt:', cookies.length);
  const cUser = cookies.find(c => c.name === 'c_user');
  if (cUser) {
    console.log('c_user cookie found:', cUser.value);
    console.log('LOGIN SUCCESS!');
  } else {
    console.log('No c_user cookie - not logged in');
  }

  // If logged in, let's navigate to marketplace and messages
  if (cUser) {
    console.log('\nNavigating to marketplace...');
    await page.goto('https://www.facebook.com/marketplace');
    await page.waitForTimeout(5000);
    await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_marketplace_loggedin.png' });
    
    console.log('Navigating to marketplace messages...');
    await page.goto('https://www.facebook.com/marketplace/messages');
    await page.waitForTimeout(5000);
    await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_mp_messages.png' });
    
    const msgContent = await page.textContent('body');
    console.log('Message page content length:', msgContent.length);
    
    // Search for condo
    const condoRegex = /condo[^<]{0,500}/gi;
    const matches = msgContent.match(condoRegex);
    
    if (matches && matches.length > 0) {
      console.log('\n=== CONDO MENTIONS FOUND ===');
      matches.forEach((m, i) => console.log(`${i+1}. ${m.substring(0, 400)}`));
    } else {
      console.log('\nNo condo mentions found');
      console.log('First 2000 chars of message page:');
      console.log(msgContent.substring(0, 2000));
    }
  }

  await browser.close();
  console.log('\n=== SCRIPT COMPLETE ===');
})();