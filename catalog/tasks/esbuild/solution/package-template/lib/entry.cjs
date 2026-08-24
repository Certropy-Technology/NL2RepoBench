const path = require('node:path');
process.env.ESBUILD_BINARY_PATH = path.join(__dirname, '..', 'bin', 'esbuild-native');
module.exports = require('./main.js');
