// Source inspection only: parse the pinned simulation without executing it.
'use strict';
const fs = require('fs'), path = require('path'), Module = require('module'), crypto = require('crypto');
const parser = new Module('acorn');
parser._compile(process.binding('natives')['internal/deps/acorn/acorn/dist/acorn'], 'acorn.js');
const input = path.join(__dirname, '../astelia_snapshot/formation_sim.js');
const source = fs.readFileSync(input, 'utf8');
const ast = parser.exports.parse(source, {ecmaVersion:2022, locations:true});
const body = ast.body[0].expression.callee.body.body;
const functions = [], fields = {}, apiNames = [];
function walk(n, owner) {
  if (!n || typeof n !== 'object') return;
  if (n.type === 'MemberExpression' && !n.computed) {
    const name = n.property.name;
    const entry = fields[name] ||= {static_occurrences:0, functions:new Set(), first_line:n.loc.start.line};
    entry.static_occurrences++; if (owner) entry.functions.add(owner);
  }
  for (const [key, value] of Object.entries(n)) {
    if (key === 'loc') continue;
    if (Array.isArray(value)) for (const child of value) walk(child, owner);
    else if (value && typeof value === 'object') walk(value, owner);
  }
}
for (const n of body) {
  if (n.type === 'FunctionDeclaration') {
    functions.push({name:n.id.name, line:n.loc.start.line, end_line:n.loc.end.line,
      parameters:n.params.map(p=>source.slice(p.start,p.end))}); walk(n,n.id.name);
  } else if (n.type === 'VariableDeclaration') {
    for (const d of n.declarations) {
      if (d.id.name === 'api') for (const p of d.init.properties) apiNames.push(p.key.name);
      if (d.init && ['FunctionExpression','ArrowFunctionExpression'].includes(d.init.type)) {
        functions.push({name:d.id.name,line:d.loc.start.line,end_line:d.loc.end.line,
          parameters:d.init.params.map(p=>source.slice(p.start,p.end))}); walk(d,d.id.name);
      } else walk(d,d.id.name);
    }
  } else walk(n,'table/combo callbacks');
}
const result = {schema:1, source_sha256:crypto.createHash('sha256').update(source).digest('hex'),
  policy:'Static occurrence counts are an access inventory, not a runtime profile.',
  functions, exports:apiNames, fields:Object.fromEntries(Object.entries(fields).sort().map(([k,v])=>
    [k,{...v,functions:[...v.functions].sort()}]))};
fs.writeFileSync(path.join(__dirname,'native_source_inventory.json'),JSON.stringify(result,null,2)+'\n');
