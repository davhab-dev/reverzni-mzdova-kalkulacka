'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');

const html = fs.readFileSync(new URL('../index.html', 'file://' + __filename), 'utf8');

function extractFunction(name) {
  const marker = 'function ' + name + '(';
  const start = html.indexOf(marker);
  assert.notEqual(start, -1, 'missing production function: ' + name);
  const open = html.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < html.length; i++) {
    if (html[i] === '{') depth++;
    if (html[i] === '}') {
      depth--;
      if (depth === 0) return html.slice(start, i + 1);
    }
  }
  throw new Error('unclosed function: ' + name);
}

const production = new Function(
  'const MAX_AMOUNT=100000000;\n' +
  extractFunction('childCredit') + '\n' +
  extractFunction('calc') + '\n' +
  extractFunction('reverse') + '\n' +
  'return { childCredit, calc, reverse };'
)();

const standard = { credit: true, children: 0, ztppChildren: 0, invalidity: 0, ztpp: false };
const noCredits = { ...standard, credit: false };

test('child tax credit follows birth order and doubles ZTP/P child amount', () => {
  assert.equal(production.childCredit(1, 0), 1267);
  assert.equal(production.childCredit(2, 0), 3127);
  assert.equal(production.childCredit(3, 1), 7767);
  assert.equal(production.childCredit(3, 3), 10894);
  assert.equal(production.childCredit(0, 5), 0);
});

test('gross-to-net basic payroll arithmetic', () => {
  const result = production.calc(10000, noCredits);
  assert.equal(result.social, 710);
  assert.equal(result.health, 450);
  assert.equal(result.taxBase, 10000);
  assert.equal(result.taxBeforeCredit, 1500);
  assert.equal(result.net, 7340);
});

test('taxpayer credit reduces tax but never below zero', () => {
  const result = production.calc(10000, standard);
  assert.equal(result.taxAfterPersonal, 0);
  assert.equal(result.net, 8840);
});

test('child credit creates eligible monthly bonus at gross threshold', () => {
  const result = production.calc(20000, { ...standard, children: 1 });
  assert.equal(result.taxBonus, 837);
  assert.equal(result.net, 18517);
  assert.equal(production.calc(11199, { ...standard, children: 1 }).bonusEligible, false);
  assert.equal(production.calc(11200, { ...standard, children: 1 }).bonusEligible, true);
});

test('higher tax rate applies above 2026 monthly threshold', () => {
  const below = production.calc(146800, noCredits);
  const above = production.calc(146901, noCredits);
  assert.equal(below.taxBase, 146800);
  assert.equal(above.taxBase, 147000);
  assert.equal(above.taxBeforeCredit, 22058);
});

test('net-to-gross returns the lowest gross amount meeting target net', () => {
  const target = 15000;
  const result = production.reverse(target, standard);
  assert.ok(result.net >= target);
  assert.ok(production.calc(result.gross - 1, standard).net < target);
});

test('reverse calculation rejects non-finite and unsupported targets', () => {
  assert.equal(production.reverse(Infinity, standard), null);
  assert.equal(production.reverse(100000001, standard), null);
});

test('UI rejects unsupported amounts before reverse calculation', () => {
  assert.match(html, /id="amount"[^>]*max="100000000"/);
  assert.match(html, /if\(raw>MAX_AMOUNT\)/);
  assert.match(html, /const MAX_AMOUNT=100000000/);
});

test('source audit fails closed when calendar year exceeds audited constants', () => {
  const checker = fs.readFileSync(new URL('../scripts/check_sources.py', 'file://' + __filename), 'utf8');
  assert.match(checker, /if year != 2026:/);
  assert.match(checker, /parameter set is for 2026/);
});
