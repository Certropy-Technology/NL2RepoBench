import { PassThrough } from 'node:stream';
import * as fsStat from '@nodelib/fs.stat';
import * as fsWalk from '@nodelib/fs.walk';
import { Reader } from './reader.js';
export class ReaderStream extends Reader {
    _walkStream = fsWalk.walkStream;
    _stat = fsStat.stat;
    async #getEntry(filepath, pattern, options) {
        return this.#getStat(filepath)
            .then((stats) => this._makeEntry(stats, pattern))
            .catch((error) => {
            if (options.errorFilter(error)) {
                return undefined;
            }
            throw error;
        });
    }
    async #getStat(filepath) {
        return new Promise((resolve, reject) => {
            this._stat(filepath, this._fsStatSettings, (error, stats) => {
                if (error === null) {
                    resolve(stats);
                }
                else {
                    reject(error);
                }
            });
        });
    }
    dynamic(root, options) {
        return this._walkStream(root, options);
    }
    static(patterns, options) {
        const filepaths = patterns.map((pattern) => this._getFullEntryPath(pattern));
        const stream = new PassThrough({ objectMode: true, signal: options.signal });
        stream._write = (index, _enc, done) => {
            this.#getEntry(filepaths[index], patterns[index], options)
                .then((entry) => {
                if (entry !== undefined && options.entryFilter(entry)) {
                    stream.push(entry);
                }
                if (index === filepaths.length - 1) {
                    stream.end();
                }
                done();
            })
                .catch(done);
        };
        for (let index = 0; index < filepaths.length; index++) {
            stream.write(index);
        }
        return stream;
    }
}
