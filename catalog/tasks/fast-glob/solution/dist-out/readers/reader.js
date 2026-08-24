import * as path from 'node:path';
import * as fsStat from '@nodelib/fs.stat';
import * as utils from '../utils/index.js';
export class Reader {
    #settings;
    _fsStatSettings;
    constructor(settings) {
        this.#settings = settings;
        this._fsStatSettings = new fsStat.Settings({
            followSymbolicLink: settings.followSymbolicLinks,
            fs: settings.fs,
            throwErrorOnBrokenSymbolicLink: settings.throwErrorOnBrokenSymbolicLink,
        });
    }
    _getFullEntryPath(filepath) {
        return path.resolve(this.#settings.cwd, filepath);
    }
    _makeEntry(stats, pattern) {
        const entry = {
            name: pattern,
            path: pattern,
            dirent: utils.fs.createDirentFromStats(pattern, stats),
        };
        if (this.#settings.stats) {
            entry.stats = stats;
        }
        return entry;
    }
    _isFatalError(error) {
        return !utils.errno.isEnoentCodeError(error) && !this.#settings.suppressErrors;
    }
}
