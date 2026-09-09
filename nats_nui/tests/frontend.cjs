const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const code = fs.readFileSync(path.join(__dirname, '../ha-init.js'), 'utf8');
function run(values = {}) {
  vm.runInNewContext(code, {localStorage: {
    getItem: key => values[key] ?? null,
    setItem: (key,value) => {values[key]=value;},
  }});
  return values;
}
const fresh = run();
assert.deepEqual(JSON.parse(fresh['docs-state']), {});
assert.deepEqual(JSON.parse(fresh['cards-all']), []);
const saved = {'docs-state':'{"drawerPosition":"right"}', 'cards-all':'[{"uuid":"saved"}]', 'unrelated':'keep'};
assert.equal(run(saved)['docs-state'], '{"drawerPosition":"right"}');
assert.equal(saved['cards-all'], '[{"uuid":"saved"}]');
assert.equal(saved.unrelated, 'keep');
assert.equal(run({'docs-state':'invalid','cards-all':'null'})['cards-all'], '[]');
vm.runInNewContext(code, {localStorage: {getItem(){throw new Error('blocked');}}});
console.log('PASS: fresh, saved, corrupt and restricted browser storage');
