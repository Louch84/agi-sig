const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('Navigating to Facebook...');
  await page.goto('https://www.facebook.com');

  // Check if logged in
  await page.waitForTimeout(2000);
  const url = page.url();
  console.log('Current URL:', url);

  // Check for login form
  const emailInput = await page.$('input[name="email"]');
  if (emailInput) {
    console.log('Not logged in, logging in...');
    await page.fill('input[name="email"]', '2152848650');
    await page.fill('input[name="pass"]', 'Conquerer4891');
    await page.click('button[name="login"]');
    await page.waitForTimeout(3000);
  }

  console.log('URL after login attempt:', page.url());

  // Navigate to Marketplace
  console.log('Going to Marketplace...');
  await page.goto('https://www.facebook.com/marketplace');
  await page.waitForTimeout(3000);

  console.log('URL:', page.url());

  // Look for messages about condo
  // First try to find message icon or messaging section
  console.log('Looking for messages...');

  // Try clicking messages icon
  const messagesIcon = await page.$('a[href*="/messages"]');
  if (messagesIcon) {
    console.log('Found messages link');
  }

  // Check page content for any condo-related text
  const pageContent = await page.textContent('body');
  console.log('Page loaded, checking for condo listings...');

  // Try to find Marketplace messages specifically
  // Facebook Marketplace has a "Messages" tab
  try {
    const messagesTab = await page.$('a[href*="marketplace/messages"]');
    if (messagesTab) {
      console.log('Found marketplace messages tab');
      await messagesTab.click();
      await page.waitForTimeout(2000);
    }
  } catch(e) {
    console.log('Could not find marketplace messages tab:', e.message);
  }

  // Try going directly to marketplace messages
  console.log('Trying marketplace messages URL...');
  await page.goto('https://www.facebook.com/marketplace/messages');
  await page.waitForTimeout(3000);

  console.log('Messages page URL:', page.url());

  // Get page content to see what we have
  const messagesContent = await page.textContent('body');
  console.log('Messages page content length:', messagesContent.length);

  // Look for anything about "condo"
  if (messagesContent.toLowerCase().includes('condo')) {
    console.log('Found condo mentions on page!');
    // Get the text around condo mentions
    const condoIndex = messagesContent.toLowerCase().indexOf('condo');
    console.log('Condo context:', messagesContent.substring(Math.max(0, condoIndex - 200), condoIndex + 500));
  }

  // Take a screenshot
  await page.screenshot({ path: '/Users/sigbotti/.openclaw/workspace/facebook_marketplace.png' });
  console.log('Screenshot saved');

  await browser.close();
  console.log('Done');
})();