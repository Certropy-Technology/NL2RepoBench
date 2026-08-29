import {join} from 'node:path';
import {spawnSync} from 'node:child_process';

const NODE = process.execPath;
const ADAPTER = String.raw`
import {readFileSync} from 'node:fs';
const api = await import('css-tree');
const plain = value => value == null ? value : api.toPlainObject(value);
function fail(message, error) {
  process.stdout.write(JSON.stringify({ok:false, message:String(message).slice(0,2048), errorType:error?.constructor?.name ?? 'Error'})+'\n');
}
function main(request) {
  if (!request || typeof request !== 'object' || Array.isArray(request)) throw new Error('malformed request');
  const p = request.payload ?? {};
  if (request.operation === 'shape') {
    const names = ['parse','generate','tokenize','walk','find','findLast','findAll','toPlainObject','fromPlainObject','clone','lexer','definitionSyntax','ident','string','url','tokenNames','tokenTypes','version','List','Lexer','TokenStream','OffsetToLocation','createSyntax','createLexer','fork'];
    return {keys:Object.keys(api).sort(), types:Object.fromEntries(names.map(name => [name, typeof api[name]])), version:api.version};
  }
  if (request.operation === 'parse-generate') {
    const ast = api.parse(p.source, p.options ?? {});
    const object = plain(ast);
    const roundTrip = p.roundTrip === true ? api.generate(api.fromPlainObject(object)) : null;
    return {ast:object, generated:api.generate(ast), roundTrip};
  }
  if (request.operation === 'tokens') {
    const source = String(p.source ?? '');
    const tokens = [];
    api.tokenize(source, (type, start, end) => tokens.push({type, name:api.tokenNames[type], raw:source.slice(start,end)}));
    return tokens;
  }
  if (request.operation === 'walk') {
    const ast = api.parse(p.source, p.options ?? {});
    const nodes = [];
    api.walk(ast, {visit:p.visit, reverse:p.reverse === true, enter(node) { nodes.push({type:node.type, name:node.name ?? null, property:node.property ?? null, value:node.value ?? null}); }});
    return nodes;
  }
  if (request.operation === 'find') {
    const ast = api.parse(p.source, p.options ?? {});
    const predicate = node => node.type === p.nodeType;
    const first = api.find(ast, predicate);
    const last = api.findLast(ast, predicate);
    const all = api.findAll(ast, predicate);
    return {first:plain(first ?? null), last:plain(last ?? null), all:all.map(plain)};
  }
  if (request.operation === 'definition') {
    const ast = api.definitionSyntax.parse(p.source);
    const nodes = [];
    if (p.walk === true) api.definitionSyntax.walk(ast, {enter(node) { nodes.push({type:node.type, name:node.name ?? null, value:node.value ?? null}); }});
    return {ast:plain(ast), generated:api.definitionSyntax.generate(ast), nodes};
  }
  if (request.operation === 'lexer') {
    const ast = api.parse(p.value, {context:'value'});
    const result = api.lexer.matchProperty(p.property, ast);
    return {matched:plain(result.matched ?? null), iterations:result.iterations, error:result.error ? String(result.error.message ?? result.error) : null};
  }
  if (request.operation === 'utils') {
    const fn = api[p.namespace]?.[p.method];
    if (typeof fn !== 'function') throw new Error('utility is not allowlisted');
    return fn(p.value, p.apostrophe === true);
  }
  throw new Error('operation is not allowlisted');
}
try {
  const request = JSON.parse(readFileSync(0, 'utf8'));
  process.stdout.write(JSON.stringify({ok:true, value:main(request)})+'\n');
} catch (error) { fail(error?.message ?? error, error); }
`;

export function call(request) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error('candidate site is not configured');
  const result = spawnSync('/usr/bin/timeout', [
    '--signal=TERM','--kill-after=5s','30s','runuser','-u','candidate','--',
    '/usr/bin/prlimit','--cpu=30','--nproc=32','--nofile=128','--',
    'env','-i','PATH=/usr/local/bin:/usr/bin:/bin',`HOME=${site}/home`,`TMPDIR=${site}/tmp`,
    NODE,'--no-addons','--input-type=module','--eval',ADAPTER,
  ], {cwd:site,input:JSON.stringify(request),encoding:'utf8',maxBuffer:256*1024,timeout:35_000});
  if (result.error || !result.stdout) throw new Error(`candidate child failed: ${result.error?.message ?? `status=${result.status}`}`);
  try { return JSON.parse(result.stdout); } catch { throw new Error('candidate child returned malformed JSON'); }
}
