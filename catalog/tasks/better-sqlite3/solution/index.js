'use strict';

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { DatabaseSync } = require('node:sqlite');

class SqliteError extends Error {
  constructor(message, code) {
    super(message);
    this.name = 'SqliteError';
    this.code = code;
  }
}

function sqliteError(error) {
  if (error instanceof SqliteError) return error;
  const message = String(error?.message ?? error);
  const code = /UNIQUE constraint failed/i.test(message)
    ? 'SQLITE_CONSTRAINT_UNIQUE'
    : /attempt to write a readonly database/i.test(message)
      ? 'SQLITE_READONLY'
      : error?.code;
  const wrapped = new SqliteError(message, code);
  wrapped.cause = error;
  return wrapped;
}

function validBoolean(value, name) {
  if (value !== undefined && typeof value !== 'boolean') throw new TypeError(`${name} must be boolean`);
}

class Statement {
  constructor(database, sql) {
    this.database = database;
    this.sql = sql;
    this.statement = database.handle.prepare(sql);
    this.plucked = false;
    this.rawRows = false;
    this.bigInts = false;
    this.bound = null;
  }

  _check() { this.database._check(); }
  _args(args) {
    if (this.bound !== null && args.length) throw new TypeError('statement already has bound parameters');
    const values = this.bound === null ? args : this.bound;
    if (values.length === 1 && values[0] && typeof values[0] === 'object' && !Buffer.isBuffer(values[0]) && !Array.isArray(values[0])) return values;
    return values;
  }
  _configure() {
    this.statement.setAllowBareNamedParameters(true);
    this.statement.setAllowUnknownNamedParameters(false);
    this.statement.setReturnArrays(this.rawRows);
    this.statement.setReadBigInts(this.bigInts);
  }
  _shape(row) {
    if (row === undefined) return row;
    if (this.plucked) return Array.isArray(row) ? row[0] : Object.values(row)[0];
    return row;
  }
  run(...args) {
    this._check(); this._configure();
    try { return this.statement.run(...this._args(args)); }
    catch (error) { throw sqliteError(error); }
  }
  get(...args) {
    this._check(); this._configure();
    try { return this._shape(this.statement.get(...this._args(args))); }
    catch (error) { throw sqliteError(error); }
  }
  all(...args) {
    this._check(); this._configure();
    try { return this.statement.all(...this._args(args)).map((row) => this._shape(row)); }
    catch (error) { throw sqliteError(error); }
  }
  *iterate(...args) {
    this._check(); this._configure();
    try {
      for (const row of this.statement.iterate(...this._args(args))) yield this._shape(row);
    } catch (error) { throw sqliteError(error); }
  }
  bind(...args) { this._check(); if (this.bound !== null) throw new TypeError('already bound'); this.bound = args; return this; }
  pluck(toggle = true) { validBoolean(toggle, 'pluck'); this.plucked = toggle; return this; }
  raw(toggle = true) { validBoolean(toggle, 'raw'); this.rawRows = toggle; return this; }
  safeIntegers(toggle = true) { validBoolean(toggle, 'safeIntegers'); this.bigInts = toggle; return this; }
  expand(toggle = true) { validBoolean(toggle, 'expand'); return this; }
  columns() { this._check(); this._configure(); return this.statement.columns(); }
  toString() { return this.sql; }
}

class Database {
  constructor(filename = '', options = {}) {
    if (typeof filename !== 'string' && !Buffer.isBuffer(filename)) throw new TypeError('filename must be a string or Buffer');
    if (!options || typeof options !== 'object' || Array.isArray(options)) throw new TypeError('options must be an object');
    validBoolean(options.readonly, 'readonly');
    validBoolean(options.fileMustExist, 'fileMustExist');
    validBoolean(options.timeout, 'timeout');
    try {
      this.handle = Buffer.isBuffer(filename) ? new DatabaseSync(':memory:') : new DatabaseSync(filename || ':memory:', { readOnly: options.readonly === true, timeout: options.timeout });
      if (Buffer.isBuffer(filename)) this.handle.deserialize(filename);
    } catch (error) { throw sqliteError(error); }
    this.name = Buffer.isBuffer(filename) ? ':memory:' : (filename || '');
    this.memory = this.name === ':memory:' || this.name === '';
    this.readonly = options.readonly === true;
    this.closed = false;
    this.inTransaction = false;
  }
  _check() { if (!this.open) throw new SqliteError('database connection is closed', 'SQLITE_MISUSE'); }
  get open() { return !this.closed; }
  close() { if (!this.closed) { this.handle.close(); this.closed = true; } return this; }
  exec(sql) { this._check(); if (typeof sql !== 'string') throw new TypeError('sql must be a string'); try { this.handle.exec(sql); return this; } catch (error) { throw sqliteError(error); } }
  prepare(sql) { this._check(); if (typeof sql !== 'string' || !sql.trim()) throw new TypeError('sql must be a non-empty string'); try { return new Statement(this, sql); } catch (error) { throw sqliteError(error); } }
  pragma(sql, options = {}) { validBoolean(options.simple, 'simple'); const statement = this.prepare(`PRAGMA ${sql}`); const rows = statement.all(); if (options.simple) return rows[0] ? Object.values(rows[0])[0] : undefined; return rows; }
  function(name, options, fn) { this._check(); if (typeof options === 'function') { fn = options; options = {}; } if (typeof name !== 'string' || typeof fn !== 'function') throw new TypeError('invalid function'); this.handle.function(name, options || {}, fn); return this; }
  aggregate(name, options) { this._check(); if (typeof name !== 'string' || !options || typeof options.step !== 'function') throw new TypeError('invalid aggregate'); this.handle.aggregate(name, options); return this; }
  serialize() { this._check(); return Buffer.from(this.handle.serialize()); }
  deserialize(buffer) { this._check(); if (!Buffer.isBuffer(buffer) && !(buffer instanceof Uint8Array)) throw new TypeError('buffer required'); this.handle.deserialize(buffer); return this; }
  transaction(fn) {
    if (typeof fn !== 'function') throw new TypeError('transaction callback required');
    const run = (mode, ...args) => {
      this._check();
      const nested = this.inTransaction;
      const savepoint = `sp_${this._savepoint = (this._savepoint ?? 0) + 1}`;
      try {
        this.exec(nested ? `SAVEPOINT ${savepoint}` : `BEGIN ${mode}`);
        this.inTransaction = true;
        const result = fn(...args);
        this.exec(nested ? `RELEASE ${savepoint}` : 'COMMIT');
        this.inTransaction = nested;
        return result;
      } catch (error) {
        try { this.exec(nested ? `ROLLBACK TO ${savepoint}; RELEASE ${savepoint}` : 'ROLLBACK'); } finally { this.inTransaction = nested; }
        throw error;
      }
    };
    const wrapper = (...args) => run('DEFERRED', ...args);
    wrapper.default = wrapper;
    wrapper.deferred = (...args) => run('DEFERRED', ...args);
    wrapper.immediate = (...args) => run('IMMEDIATE', ...args);
    wrapper.exclusive = (...args) => run('EXCLUSIVE', ...args);
    return wrapper;
  }
}

function scenario(name) {
  const db = new Database(':memory:');
  try {
    if (name === 'basic') { db.exec("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT); INSERT INTO users(name) VALUES ('Ada'), ('Linus');"); return { rows: db.prepare('SELECT id, name FROM users ORDER BY id').all(), count: 2, open: db.open }; }
    if (name === 'bindings') { db.exec('CREATE TABLE items(a TEXT, b INTEGER)'); const s = db.prepare('INSERT INTO items VALUES (?, ?)'); const positional = s.run('x', 7); const named = db.prepare('INSERT INTO items VALUES (@a, :b)').run({ a: 'y', b: 8 }); return { positional: positional.changes, named: named.changes, changes: db.prepare('SELECT COUNT(*) AS n FROM items').pluck().get() }; }
    if (name === 'iteration') { db.exec('CREATE TABLE items(value INTEGER); INSERT INTO items VALUES (3),(1),(2)'); return { values: [...db.prepare('SELECT value FROM items ORDER BY value').pluck().iterate()] }; }
    if (name === 'transactions') { db.exec('CREATE TABLE events(value TEXT)'); const add = db.transaction((value) => db.prepare('INSERT INTO events VALUES (?)').run(value)); add('committed'); const failing = db.transaction(() => { db.prepare('INSERT INTO events VALUES (?)').run('rolledBack'); throw new Error('outer rollback'); }); try { failing(); } catch {} const inner = db.transaction(() => { db.prepare('INSERT INTO events VALUES (?)').run('inner'); throw new Error('inner'); }); const outer = db.transaction(() => { db.prepare('INSERT INTO events VALUES (?)').run('outer'); try { inner(); } catch {} }); outer(); return { committed: db.prepare("SELECT value FROM events WHERE value = 'committed'").pluck().get(), rolledBack: db.prepare("SELECT COUNT(*) FROM events WHERE value = 'rolledBack'").pluck().get(), nested: db.prepare('SELECT value FROM events ORDER BY rowid').pluck().all() }; }
    if (name === 'functions') { db.function('double', { deterministic: true }, (x) => x * 2); db.aggregate('sum_values', { start: 0, step: (total, value) => total + value, result: (total) => total }); return { scalar: db.prepare('SELECT double(4) AS value').pluck().get(), aggregate: db.prepare('SELECT sum_values(value) AS value FROM (SELECT 2 value UNION ALL SELECT 3)').pluck().get() }; }
    if (name === 'pragma') { db.pragma('foreign_keys = ON'); return { foreignKeys: db.pragma('foreign_keys', { simple: true }), cacheSizeType: typeof db.pragma('cache_size', { simple: true }) }; }
    if (name === 'serialization') { db.exec("CREATE TABLE items(value TEXT); INSERT INTO items VALUES ('saved')"); const before = db.prepare('SELECT value FROM items').pluck().get(); const copy = new Database(db.serialize()); const after = copy.prepare('SELECT value FROM items').pluck().get(); copy.close(); return { before, after }; }
    if (name === 'errors') { db.exec('CREATE TABLE items(value TEXT UNIQUE)'); db.prepare('INSERT INTO items VALUES (?)').run('x'); let constraintCode; try { db.prepare('INSERT INTO items VALUES (?)').run('x'); } catch (error) { constraintCode = error.code; } db.close(); let closedError; try { db.exec('SELECT 1'); } catch (error) { closedError = error.code; } return { constraintCode, closedError }; }
    if (name === 'statementModes') { db.exec("CREATE TABLE items(a INTEGER, b TEXT); INSERT INTO items VALUES (42, 'x')"); const pluck = db.prepare('SELECT b FROM items').pluck().get(); const raw = db.prepare('SELECT a, b FROM items').raw().get(); const safeIntegerType = typeof db.prepare('SELECT a FROM items').safeIntegers().pluck().get(); return { pluck, raw, safeIntegerType }; }
    if (name === 'columns') { const columns = db.prepare('SELECT 1 AS first, 2 AS second'); return { names: columns.columns().map((column) => column.name), count: columns.columns().length }; }
    if (name === 'readonly') { const file = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'better-sqlite3-')), 'db.sqlite'); const writable = new Database(file); writable.exec('CREATE TABLE items(value TEXT)'); writable.close(); const readOnly = new Database(file, { readonly: true }); let writeCode; try { readOnly.exec('CREATE TABLE blocked(value TEXT)'); } catch (error) { writeCode = error.code; } const result = { readonly: readOnly.readonly, writeCode }; readOnly.close(); return result; }
    if (name === 'apiShape') return { hasDatabase: typeof Database === 'function', hasSqliteError: typeof SqliteError === 'function', methods: ['prepare', 'exec', 'pragma', 'transaction', 'function', 'aggregate', 'serialize', 'close'].filter((method) => typeof db[method] === 'function') };
    throw new TypeError(`unknown scenario: ${name}`);
  } finally { if (db.open) db.close(); }
}

module.exports = Database;
module.exports.Database = Database;
module.exports.SqliteError = SqliteError;
module.exports.runScenario = scenario;
