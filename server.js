const express = require('express');

const app = express();

app.use(express.static('docs'));

app.get('/api', (req, res) => {
  res.send('Successful response.');
});

const blocks = {};

app.get('/api/blocks', (req, res) => {
  const count = Object.keys(blocks).length;
  res.send(JSON.stringify({count}));
});

const transactions = [];
app.get('/api/transactions', (req, res) => {
  const head = transactions.slice(0, 100);
  res.send(JSON.stringify({count: head.length, transactions: head}));
});
app.post('/api/transactions', (req, res) => {
  const { source, target, amount } = JSON.parse(req.body);
  const transaction = {
    source: Number.parseInt(source),
    target: Number.parseInt(target),
    amount: Number.parseInt(amount),
  }
  transactions.push(transaction);
  res.send(JSON.stringify({transaction, count: transaction.length}));
});

try {
  app.listen(80, () => console.log('Example app is listening on port 80.'));
} catch (e) {
  app.listen(3000, () => console.log('Example app is listening on port 3000.'));
}
