'use strict';

const Database = require('./database');
const SqliteError = require('./sqlite-error');

Database.SqliteError = SqliteError;
Database.runScenario = require('./scenarios');
module.exports = Database;
module.exports.Database = Database;
module.exports.SqliteError = SqliteError;
module.exports.runScenario = Database.runScenario;
