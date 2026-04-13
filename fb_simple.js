const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('Going to Facebook...');
  await page.goto('https://www.facebook.com');
  await page.waitForTimeout(3000);

  // Credentials from environment variables
  const fbEmail = process.env.FB_EMAIL || '';
  const fbPass = process.env.FB_PASS || '';

  // Check for login
  const emailInput = await page.$('input[name="email"]');
  if (emailInput) {
    if (!fbEmail || !fbPass) {
      console.log('ERROR: FB_EMAIL or FB_PASS environment variable not set.');
      await browser.close();
      process.exit(1);
    }
    console.log('Logging in...');
    await page.fill('input[name="email"]', fbEmail);
    await page.fill('input[name="pass"]', fbPass);
    await page.click('button[name="login"]');
    await page.waitForTimeout(10000);
  }

  console.log('URL:', page.url());
  await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_state.png' });

  // Check cookies
  const cookies = await page.context().cookies();
  const cUser = cookies.find(c => c.name === 'c_user');
  console.log('Logged in:', !!cUser);

  if (cUser) {
    // Go to marketplace
    await page.goto('https://www.facebook.com/marketplace');
    await page.waitForTimeout(4000);
    await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_marketplace.png' });

    // Go to messages
    await page.goto('https://www.facebook.com/marketplace/messages');
    await page.waitForTimeout(4000);
    await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/fb_messages.png' });

    const text = await page.textContent('body');
    console.log('Page text length:', text.length);

    // Look for condo
    const matches = text.match(/condo[^<]{0,500}/gi);
    if (matches && matches.length > 0) {
      console.log('Found condo mentions:', matches.length);
      matches.forEach((m, i) => console.log(`${i+1}. ${m.substring(0, 300)}`));
    } else {
      console.log('No condo mentions');
      console.log('First 2000 chars:', text.substring(0, 2000));
    }
  }

  await browser.close();
  console.log('Done');
})();