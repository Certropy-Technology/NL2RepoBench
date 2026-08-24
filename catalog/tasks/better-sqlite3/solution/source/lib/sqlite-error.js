'use strict';

class SqliteError extends Error {
  constructor(message, code = undefined) {
    super(message);
    this.name = 'SqliteError';
    if (code !== undefined) this.code = code;
  }
}

module.exports = SqliteError;
