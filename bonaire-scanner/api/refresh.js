// Start de GitHub Actions-workflow die de scraper draait.
// Vereist env vars in Vercel: GITHUB_TOKEN (fine-grained PAT, Actions: read & write op deze repo)
const REPO = 'ecommartijn/bonaire-scanner';
const WORKFLOW = 'daily_scrape.yml';
const COOLDOWN_MS = 10 * 60 * 1000;

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ message: 'Method not allowed' });
  const token = process.env.GITHUB_TOKEN;
  if (!token) return res.status(500).json({ message: 'Server niet geconfigureerd.' });
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
  };
  const base = `https://api.github.com/repos/${REPO}/actions/workflows/${WORKFLOW}`;

  const runs = await fetch(`${base}/runs?per_page=1`, { headers }).then(r => r.json());
  const last = runs.workflow_runs && runs.workflow_runs[0];
  if (last && (last.status !== 'completed' || Date.now() - new Date(last.created_at) < COOLDOWN_MS)) {
    return res.status(429).json({ message: 'Er is net al ververst of een verversing loopt. Probeer over een paar minuten opnieuw.' });
  }

  const r = await fetch(`${base}/dispatches`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ ref: 'main' }),
  });
  if (!r.ok) return res.status(502).json({ message: 'Starten mislukt.' });
  res.status(200).json({ message: 'Verversing gestart. Over ongeveer 3 minuten staat de nieuwe data online, herlaad dan de pagina.' });
}
