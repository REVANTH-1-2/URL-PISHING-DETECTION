document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const targetUrl = params.get('url') || '';
  const risk = params.get('risk') || '0';
  const prediction = params.get('prediction') || 'PHISHING';
  let factors = [];

  try {
    factors = JSON.parse(params.get('factors') || '[]');
  } catch (e) {
    factors = [];
  }

  document.getElementById('blockedUrl').textContent = targetUrl;
  document.getElementById('riskScoreVal').textContent = `${risk}%`;
  document.getElementById('verdictVal').textContent = prediction;

  const reasonsList = document.getElementById('reasonsList');
  reasonsList.innerHTML = '';

  if (factors.length > 0) {
    factors.forEach((f) => {
      const li = document.createElement('li');
      li.className = 'reason-item';
      li.textContent = `• [${f.severity}] ${f.factor}: ${f.explanation}`;
      reasonsList.appendChild(li);
    });
  } else {
    const li = document.createElement('li');
    li.className = 'reason-item';
    li.textContent = '• High-risk domain indicators and suspicious structural patterns detected.';
    reasonsList.appendChild(li);
  }

  // Go Back
  document.getElementById('btnBack').addEventListener('click', () => {
    if (window.history.length > 1) {
      window.history.back();
    } else {
      window.location.href = 'https://www.google.com';
    }
  });

  // Proceed Anyway (Unsafe)
  document.getElementById('btnProceed').addEventListener('click', () => {
    if (confirm('Warning: Proceeding to this site may expose your passwords or banking credentials. Are you sure?')) {
      chrome.runtime.sendMessage({ action: 'ALLOW_URL', url: targetUrl });
    }
  });
});
