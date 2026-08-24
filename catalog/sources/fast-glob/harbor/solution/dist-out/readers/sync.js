import * as fsStat from '@nodelib/fs.stat';
import * as fsWalk from '@nodelib/fs.walk';
import { Reader } from './reader.js';
export class ReaderSync extends Reader {
    _walkSync = fsWalk.walkSync;
    _statSync = fsStat.statSync;
    #getEntry(filepath, pattern, options) {
        try {
            const stats = this.#getStat(filepath);
            return this._makeEntry(stats, pattern);
        }
        catch (error) {
            if (options.errorFilter(error)) {
                return undefined;
            }
            throw error;
        }
    }
    #getStat(filepath) {
        return this._statSync(filepath, this._fsStatSettings);
    }
    dynamic(root, options) {
        return this._walkSync(root, options);
    }
    static(patterns, options) {
        const entries = [];
        for (const pattern of patterns) {
            const filepath = this._getFullEntryPath(pattern);
            const entry = this.#getEntry(filepath, pattern, options);
            if (entry === undefined || !options.entryFilter(entry)) {
                continue;
            }
            entries.push(entry);
        }
        return entries;
    }
}
