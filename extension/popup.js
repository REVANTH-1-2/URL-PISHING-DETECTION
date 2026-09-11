document.addEventListener('DOMContentLoaded', async () => {
  const urlDisplay = document.getElementById('urlDisplay');
  const scanBtn = document.getElementById('scanBtn');
  const btnText = document.getElementById('btnText');
  const btnIcon = document.getElementById('btnIcon');
  const resultsCard = document.getElementById('resultsCard');
  const riskScore = document.getElementById('riskScore');
  const predictionBadge = document.getElementById('predictionBadge');
  const confidenceText = document.getElementById('confidenceText');
  const riskFactorsList = document.getElementById('riskFactorsList');
  const recommendationText = document.getElementById('recommendationText');
  const apiInput = document.getElementById('apiInput');

  let currentTabUrl = '';

  // Get active tab URL
  if (typeof chrome !== 'undefined' && chrome.tabs) {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab && tab.url) {
        currentTabUrl = tab.url;
        urlDisplay.textContent = currentTabUrl;
      } else {
        urlDisplay.textContent = 'Unable to get current tab URL';
      }
    } catch (e) {
      currentTabUrl = window.location.href;
      urlDisplay.textContent = currentTabUrl;
    }
  } else {
    currentTabUrl = 'https://www.google.com';
    urlDisplay.textContent = currentTabUrl;
  }

  // Load saved API endpoint
  if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get(['apiServer'], (res) => {
      if (res.apiServer) apiInput.value = res.apiServer;
    });
  }

  apiInput.addEventListener('change', () => {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      chrome.storage.local.set({ apiServer: apiInput.value.trim() });
    }
  });

  // Scan handler
  scanBtn.addEventListener('click', async () => {
    if (!currentTabUrl || currentTabUrl.startsWith('chrome://')) {
      alert('Cannot scan browser internal pages.');
      return;
    }

    const baseUrl = apiInput.value.trim().replace(/\/+$/, '');
    const apiUrl = `${baseUrl}/api/scan/url`;

    scanBtn.disabled = true;
    btnText.textContent = 'Scanning...';
    btnIcon.textContent = '⏳';

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: currentTabUrl }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      displayResults(data);
    } catch (err) {
      alert(`Scan failed: ${err.message}\nMake sure your backend API (${baseUrl}) is running.`);
    } finally {
      scanBtn.disabled = false;
      btnText.textContent = 'Scan Current Page';
      btnIcon.textContent = '🔍';
    }
  });

  function displayResults(data) {
    resultsCard.classList.remove('hidden');

    const score = Math.round(data.risk_score);
    riskScore.textContent = `${score}%`;

    // Gauge border color
    const gauge = document.querySelector('.risk-gauge');
    if (score >= 70) {
      gauge.style.borderColor = '#ef4444';
    } else if (score >= 35) {
      gauge.style.borderColor = '#f59e0b';
    } else {
      gauge.style.borderColor = '#10b981';
    }

    // Prediction badge
    predictionBadge.textContent = data.prediction;
    predictionBadge.className = 'badge';
    if (data.prediction === 'PHISHING') {
      predictionBadge.classList.add('badge-phishing');
    } else if (data.prediction === 'SUSPICIOUS') {
      predictionBadge.classList.add('badge-suspicious');
    } else {
      predictionBadge.classList.add('badge-safe');
    }

    confidenceText.textContent = `Confidence: ${Math.round(data.confidence)}%`;

    // Risk Factors
    riskFactorsList.innerHTML = '';
    if (data.risk_factors && data.risk_factors.length > 0) {
      data.risk_factors.forEach((rf) => {
        const li = document.createElement('li');
        li.className = `risk-item ${rf.severity.toLowerCase()}`;
        li.textContent = `• [${rf.severity}] ${rf.factor}: ${rf.explanation}`;
        riskFactorsList.appendChild(li);
      });
    } else {
      const li = document.createElement('li');
      li.className = 'risk-item info';
      li.textContent = '✓ No suspicious signals detected.';
      riskFactorsList.appendChild(li);
    }

    // Recommendations
    if (data.recommendations && data.recommendations.length > 0) {
      recommendationText.textContent = data.recommendations.join(' ');
    } else {
      recommendationText.textContent = 'This URL appears safe for normal browsing.';
    }
  }
});
