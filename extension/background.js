// DeepShield AI Background Real-Time Phishing Scanner & Blocker

const DEFAULT_API = "http://127.0.0.1:8000";
const scannedCache = new Map(); // url -> scanResult
const allowedUrls = new Set();  // user manually allowed URLs

// Helper to get configured API base
async function getApiServer() {
  return new Promise((resolve) => {
    chrome.storage.local.get(["apiServer"], (res) => {
      const server = res.apiServer || DEFAULT_API;
      resolve(server.replace(/\/+$/, ""));
    });
  });
}

// Auto-scan on tab navigation
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status !== "loading" || !tab.url) return;

  const targetUrl = tab.url;

  // Ignore internal/safe browser URLs
  if (
    targetUrl.startsWith("chrome://") ||
    targetUrl.startsWith("chrome-extension://") ||
    targetUrl.startsWith("about:") ||
    targetUrl.includes("localhost:") ||
    targetUrl.includes("127.0.0.1:") ||
    targetUrl.includes("onrender.com")
  ) {
    return;
  }

  // Check if user manually clicked "Proceed Anyway"
  if (allowedUrls.has(targetUrl)) return;

  // Check cache first
  if (scannedCache.has(targetUrl)) {
    const cached = scannedCache.get(targetUrl);
    if (cached.isRisky) {
      blockTab(tabId, targetUrl, cached.data);
    }
    return;
  }

  // Perform AI API scan in background
  try {
    const apiServer = await getApiServer();
    const response = await fetch(`${apiServer}/api/scan/url`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: targetUrl }),
    });

    if (!response.ok) return;

    const data = await response.json();
    const isRisky = data.prediction === "PHISHING" || data.prediction === "SUSPICIOUS" || data.risk_score >= 40.0;

    scannedCache.set(targetUrl, { isRisky, data });

    if (isRisky) {
      blockTab(tabId, targetUrl, data);
    }
  } catch (err) {
    console.warn("DeepShield background scan error:", err.message);
  }
});

function blockTab(tabId, url, data) {
  const blockPage = chrome.runtime.getURL("blocked.html");
  const params = new URLSearchParams({
    url: url,
    risk: Math.round(data.risk_score),
    prediction: data.prediction,
    factors: JSON.stringify(data.risk_factors || []),
    recs: JSON.stringify(data.recommendations || []),
  });

  chrome.tabs.update(tabId, {
    url: `${blockPage}?${params.toString()}`,
  });
}

// Allow user bypass signal from blocked page
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "ALLOW_URL" && message.url) {
    allowedUrls.add(message.url);
    if (sender.tab && sender.tab.id) {
      chrome.tabs.update(sender.tab.id, { url: message.url });
    }
    sendResponse({ success: true });
  }
});
