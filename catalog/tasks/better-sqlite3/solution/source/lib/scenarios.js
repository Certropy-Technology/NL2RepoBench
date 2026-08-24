'use strict';

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const Database = require('./database');

function withDb(fn) {
  const db = new Database(':memory:');
  try { return fn(db); } finally { db.close(); }
}

module.exports = function runScenario(name) {
  if (typeof name !== 'string') throw new TypeError('scenario name must be a string');
  switch (name) {
    case 'basic': return withDb(db => { db.exec('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)'); db.prepare('INSERT INTO users (name) VALUES (?)').run('Ada'); db.prepare('INSERT INTO users (name) VALUES (?)').run('Grace'); const rows = db.prepare('SELECT id, name FROM users ORDER BY id').all(); return { rows, count: rows.length, open: db.open }; });
    case 'bindings': return withDb(db => { db.exec('CREATE TABLE entries (value TEXT, number INTEGER)'); const insert = db.prepare('INSERT INTO entries VALUES (?, ?)'); const first = insert.run('positional', 7); const named = db.prepare('SELECT value, number FROM entries WHERE value = @value').get({ value: 'positional' }); return { positional: { value: 'positional', number: 7 }, named, changes: first.changes }; });
    case 'iteration': return withDb(db => { db.exec('CREATE TABLE numbers (value INTEGER)'); const insert = db.prepare('INSERT INTO numbers VALUES (?)'); [3, 1, 2].forEach(value => insert.run(value)); return { values: [...db.prepare('SELECT value FROM numbers ORDER BY value').pluck().iterate()] }; });
    case 'transactions': return withDb(db => { db.exec('CREATE TABLE entries (value INTEGER UNIQUE)'); db.prepare('INSERT INTO entries VALUES (1)').run(); const add = db.transaction(value => db.prepare('INSERT INTO entries VALUES (?)').run(value)); add(2); const committed = db.prepare('SELECT value FROM entries ORDER BY value').pluck().all(); const failing = db.transaction(value => { db.prepare('INSERT INTO entries VALUES (?)').run(value); db.prepare('INSERT INTO entries VALUES (1)').run(); }); try { failing(9); } catch (_) {} const rolledBack = db.prepare('SELECT value FROM entries ORDER BY value').pluck().all(); const outer = db.transaction(() => { add(3); try { add(1); } catch (_) {} add(4); }); outer(); const nested = db.prepare('SELECT value FROM entries ORDER BY value').pluck().all(); return { committed, rolledBack, nested }; });
    case 'functions': return withDb(db => { db.exec('CREATE TABLE entries (value INTEGER)'); db.prepare('INSERT INTO entries VALUES (2), (3), (4)').run(); db.function('add2', (a, b) => a + b); db.aggregate('sum_values', { start: 0, step: (total, value) => total + value }); return { scalar: db.prepare('SELECT add2(?, ?) AS value').pluck().get(3, 4), aggregate: db.prepare('SELECT sum_values(value) AS value FROM entries').pluck().get() }; });
    case 'pragma': return withDb(db => { db.pragma('foreign_keys = ON'); return { foreignKeys: db.pragma('foreign_keys', { simple: true }), cacheSizeType: typeof db.pragma('cache_size', { simple: true }) }; });
    case 'serialization': return withDb(db => { db.exec('CREATE TABLE entries (value TEXT)'); db.prepare('INSERT INTO entries VALUES (?)').run('persisted'); const before = db.prepare('SELECT value FROM entries').pluck().get(); const image = db.serialize(); const reopened = new Database(':memory:'); try { reopened.deserialize(image); const after = reopened.prepare('SELECT value FROM entries').pluck().get(); return { before, after }; } finally { reopened.close(); } });
    case 'errors': return withDb(db => { db.exec('CREATE TABLE entries (value INTEGER UNIQUE)'); db.prepare('INSERT INTO entries VALUES (1)').run(); let constraintCode = null; try { db.prepare('INSERT INTO entries VALUES (1)').run(); } catch (error) { constraintCode = error.code; } db.close(); let closedError = false; try { db.prepare('SELECT 1').get(); } catch (_) { closedError = true; } return { constraintCode, closedError }; });
    case 'statementModes': return withDb(db => { const statement = db.prepare('SELECT 7 AS value, 8 AS other'); const pluck = statement.pluck().get(); const raw = db.prepare('SELECT 7 AS value, 8 AS other').raw().get(); const safeIntegerType = typeof db.prepare('SELECT 9007199254740993 AS value').safeIntegers().pluck().get(); return { pluck, raw, safeIntegerType }; });
    case 'columns': return withDb(db => { const columns = db.prepare('SELECT 1 AS first, 2 AS second').columns(); return { names: columns.map(column => column.name), count: columns.length }; });
    case 'readonly': { const file = path.join(os.tmpdir(), 'better-sqlite3-readonly.db'); try { try { fs.unlinkSync(file); } catch (_) {} const writable = new Database(file); writable.exec('CREATE TABLE entries (value INTEGER)'); writable.close(); const readonly = new Database(file, { readonly: true }); let writeCode = null; try { readonly.prepare('INSERT INTO entries VALUES (1)').run(); } catch (error) { writeCode = error.code; } readonly.close(); return { readonly: true, writeCode }; } finally { try { fs.unlinkSync(file); } catch (_) {} } }
    case 'apiShape': return { hasDatabase: typeof Database === 'function', hasSqliteError: Boolean(Database.SqliteError), methods: ['exec', 'prepare', 'transaction', 'pragma', 'function', 'aggregate', 'serialize', 'deserialize', 'close'] };
    default: throw new Error(`unknown scenario: ${name}`);
  }
};
