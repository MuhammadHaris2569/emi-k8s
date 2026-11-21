const express = require('express');
const path = require('path');
const os = require('os');
const { MongoClient } = require('mongodb');

const MONGO_URL = process.env.MONGO_URL;
if (!MONGO_URL) { console.error('MONGO_URL is not set'); process.exit(1); }

const client = new MongoClient(MONGO_URL, { serverSelectionTimeoutMS: 8000 });
const calcs = client.db().collection('calculations');
const podName = process.env.HOSTNAME || 'unknown';

function podIp() {
  for (const list of Object.values(os.networkInterfaces()))
    for (const a of list || [])
      if (a.family === 'IPv4' && !a.internal) return a.address;
  return 'unknown';
}

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const ok = v => Number.isFinite(v) && v > 0;

app.post('/api/emi', async (req, res) => {
  const P = Number(req.body.principal);
  const rate = Number(req.body.rate);
  const n = Number(req.body.months);
  if (!ok(P) || !ok(rate) || !ok(n) || !Number.isInteger(n) || rate > 100 || n > 600)
    return res.status(400).json({ error: 'principal, rate and months must be positive numbers' });

  const r = rate / 12 / 100;
  const f = Math.pow(1 + r, n);
  const emi = (P * r * f) / (f - 1);
  const totalPayment = emi * n;
  const totalInterest = totalPayment - P;
  const round = x => Math.round(x * 100) / 100;

  try {
    await calcs.insertOne({ principal: P, rate, months: n, emi: round(emi),
                            servedBy: podName, createdAt: new Date() });
  } catch (e) {
    return res.status(503).json({ error: 'database unavailable' });
  }
  res.json({ emi: round(emi), totalPayment: round(totalPayment),
             totalInterest: round(totalInterest), servedBy: podName, podIp: podIp() });
});

app.get('/api/history', async (req, res) => {
  try {
    const rows = await calcs.find({}, { projection: { _id: 0 } })
      .sort({ createdAt: -1 }).limit(10).toArray();
    res.json(rows);
  } catch (e) { res.status(503).json({ error: 'database unavailable' }); }
});

app.get('/health', async (req, res) => {
  try { await client.db('admin').command({ ping: 1 }); res.status(200).send('OK'); }
  catch (e) { res.status(503).send('mongo unreachable'); }
});

app.listen(3000, () => console.log('EMI app listening on 3000, pod ' + podName));
