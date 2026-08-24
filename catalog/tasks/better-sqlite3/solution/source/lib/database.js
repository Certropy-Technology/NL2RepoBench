'use strict';

const { DatabaseSync } = require('node:sqlite');
const SqliteError = require('./sqlite-error');

function sqliteCall(fn) {
  try {
    return fn();
  } catch (error) {
    if (error instanceof SqliteError) throw error;
    const sqliteCodes = {
      1: 'SQLITE_ERROR',
      8: 'SQLITE_READONLY',
      14: 'SQLITE_CANTOPEN',
      19: 'SQLITE_CONSTRAINT',
      1299: 'SQLITE_CONSTRAINT_NOTNULL',
      1555: 'SQLITE_CONSTRAINT_PRIMARYKEY',
      2067: 'SQLITE_CONSTRAINT_UNIQUE',
      787: 'SQLITE_CONSTRAINT_FOREIGNKEY',
    };
    const wrapped = new SqliteError(error.message, sqliteCodes[error.errcode] || error.code);
    wrapped.cause = error;
    throw wrapped;
  }
}

function validateOptions(options) {
  if (options === undefined) return {};
  if (!options || typeof options !== 'object' || Array.isArray(options)) {
    throw new TypeError('options must be an object');
  }
  for (const key of ['readonly', 'fileMustExist', 'timeout', 'verbose']) {
    if (key in options && key !== 'verbose' && typeof options[key] !== 'boolean' && key !== 'timeout') {
      throw new TypeError(`${key} must be a boolean`);
    }
  }
  if ('timeout' in options && (!Number.isInteger(options.timeout) || options.timeout < 0)) {
    throw new TypeError('timeout must be a non-negative integer');
  }
  if ('verbose' in options && options.verbose !== null && typeof options.verbose !== 'function') {
    throw new TypeError('verbose must be a function, null, or undefined');
  }
  return options;
}

function Database(path = '', options) {
  if (!(this instanceof Database)) return new Database(path, options);
  if (path === null || path === undefined) path = '';
  if (typeof path !== 'string' && !Buffer.isBuffer(path) && !(path instanceof Uint8Array)) {
    throw new TypeError('database path must be a string or serialized database');
  }
  const opts = validateOptions(options);
  const nativeOptions = {};
  if (opts.readonly !== undefined) nativeOptions.readOnly = opts.readonly;
  if (opts.fileMustExist !== undefined) nativeOptions.readOnly = opts.fileMustExist || nativeOptions.readOnly;
  if (opts.timeout !== undefined) nativeOptions.timeout = opts.timeout;
  this._path = typeof path === 'string' ? path : ':memory:';
  this._memory = this._path === '' || this._path === ':memory:' || typeof path !== 'string';
  this._readonly = Boolean(opts.readonly);
  this._txDepth = 0;
  this._db = sqliteCall(() => new DatabaseSync(path, nativeOptions));
  if (opts.verbose) this._verbose = opts.verbose;
}

Object.defineProperties(Database.prototype, {
  name: { get() { return this._path; } },
  memory: { get() { return this._memory; } },
  readonly: { get() { return this._readonly; } },
  open: { get() { return Boolean(this._db?.isOpen); } },
  inTransaction: { get() { return Boolean(this._db?.isTransaction); } },
});

Database.prototype.exec = function exec(sql) {
  return sqliteCall(() => {
    if (typeof sql !== 'string') throw new TypeError('sql must be a string');
    this._db.exec(sql);
    return this;
  });
};

Database.prototype.prepare = function prepare(sql) {
  if (typeof sql !== 'string' || sql.length === 0) throw new TypeError('sql must be a non-empty string');
  return new Statement(this, sqliteCall(() => this._db.prepare(sql)), sql);
};

Database.prototype.pragma = function pragma(sql, options = {}) {
  if (typeof sql !== 'string') throw new TypeError('pragma must be a string');
  if (!options || typeof options !== 'object' || typeof options.simple !== 'undefined' && typeof options.simple !== 'boolean') {
    throw new TypeError('options must be an object with a boolean simple property');
  }
  const rows = this.prepare(`PRAGMA ${sql}`).all();
  if (options.simple) return rows.length ? Object.values(rows[0])[0] : undefined;
  return rows;
};

Database.prototype.function = function registerFunction(name, options, fn) {
  if (typeof options === 'function') { fn = options; options = {}; }
  if (typeof name !== 'string' || typeof fn !== 'function') throw new TypeError('invalid function definition');
  return sqliteCall(() => { this._db.function(name, options || {}, fn); return this; });
};

Database.prototype.aggregate = function registerAggregate(name, options) {
  if (typeof name !== 'string' || !options || typeof options !== 'object') throw new TypeError('invalid aggregate definition');
  return sqliteCall(() => { this._db.aggregate(name, options); return this; });
};

Database.prototype.serialize = function serialize(options) {
  const databaseName = typeof options === 'string' ? options : options?.attached || 'main';
  return sqliteCall(() => Buffer.from(this._db.serialize(databaseName)));
};

Database.prototype.deserialize = function deserialize(buffer, options) {
  if (!Buffer.isBuffer(buffer) && !(buffer instanceof Uint8Array)) throw new TypeError('buffer required');
  const databaseName = typeof options === 'string' ? options : options?.attached || 'main';
  return sqliteCall(() => { this._db.deserialize(buffer, { databaseName }); return this; });
};

Database.prototype.close = function close() {
  if (this._db?.isOpen) sqliteCall(() => this._db.close());
  return this;
};

Database.prototype.transaction = function transaction(fn) {
  if (typeof fn !== 'function') throw new TypeError('transaction requires a function');
  const make = mode => {
    const wrapped = (...args) => {
      const nested = this._txDepth > 0;
      const savepoint = `better_sqlite3_sp_${this._txDepth}`;
      this._txDepth += 1;
      try {
        if (nested) this.exec(`SAVEPOINT ${savepoint}`);
        else this.exec(`BEGIN ${mode}`);
        const result = fn.apply(this, args);
        if (nested) this.exec(`RELEASE ${savepoint}`);
        else this.exec('COMMIT');
        return result;
      } catch (error) {
        try {
          if (nested) {
            this.exec(`ROLLBACK TO ${savepoint}`);
            this.exec(`RELEASE ${savepoint}`);
          } else if (this.inTransaction) this.exec('ROLLBACK');
        } finally {
          throw error;
        }
      } finally {
        this._txDepth -= 1;
      }
    };
    return wrapped;
  };
  const result = make('');
  result.default = result;
  result.deferred = make('DEFERRED');
  result.immediate = make('IMMEDIATE');
  result.exclusive = make('EXCLUSIVE');
  return result;
};

class Statement {
  constructor(database, native, sql) {
    this.database = database;
    this._native = native;
    this.source = sql;
    this.reader = Boolean(native.columns().length);
    this.readonly = this.reader;
    this._pluck = false;
    this._raw = false;
    this._safeIntegers = false;
  }

  _args(args) {
    if (args.length === 1 && args[0] && typeof args[0] === 'object' && !Buffer.isBuffer(args[0]) && !Array.isArray(args[0])) return args[0];
    return args;
  }

  _shape(row) {
    if (row === undefined) return row;
    if (this._pluck) return Array.isArray(row) ? row[0] : Object.values(row)[0];
    if (this._raw && !Array.isArray(row)) return Object.values(row);
    return row;
  }

  run(...args) { return sqliteCall(() => this._native.run(...(Array.isArray(this._args(args)) ? this._args(args) : [this._args(args)]))); }
  get(...args) { return sqliteCall(() => this._shape(this._native.get(...(Array.isArray(this._args(args)) ? this._args(args) : [this._args(args)])))); }
  all(...args) { return sqliteCall(() => this._native.all(...(Array.isArray(this._args(args)) ? this._args(args) : [this._args(args)])).map(row => this._shape(row))); }
  iterate(...args) {
    const iterator = sqliteCall(() => this._native.iterate(...(Array.isArray(this._args(args)) ? this._args(args) : [this._args(args)])));
    return { next: () => { const item = iterator.next(); return item.done ? item : { done: false, value: this._shape(item.value) }; }, return: () => iterator.return ? iterator.return() : { done: true } , [Symbol.iterator]() { return this; } };
  }
  columns() { return sqliteCall(() => this._native.columns()); }
  pluck(toggle = true) { if (typeof toggle !== 'boolean') throw new TypeError('pluck must be boolean'); this._pluck = toggle; return this; }
  raw(toggle = true) { if (typeof toggle !== 'boolean') throw new TypeError('raw must be boolean'); this._raw = toggle; return this; }
  expand() { return this; }
  safeIntegers(toggle = true) { if (typeof toggle !== 'boolean') throw new TypeError('safeIntegers must be boolean'); this._safeIntegers = toggle; this._native.setReadBigInts(toggle); return this; }
}

module.exports = Database;
