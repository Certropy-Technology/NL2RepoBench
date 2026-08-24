import * as fsWalk from '@nodelib/fs.walk';
import { Reader } from './reader.js';
import { ReaderStream } from './stream.js';
export class ReaderAsync extends Reader {
    _walkAsync = fsWalk.walk;
    _readerStream;
    constructor(settings) {
        super(settings);
        this._readerStream = new ReaderStream(settings);
    }
    async dynamic(root, options) {
        return new Promise((resolve, reject) => {
            this._walkAsync(root, options, (error, entries) => {
                if (error === null) {
                    resolve(entries);
                }
                else {
                    reject(error);
                }
            });
        });
    }
    async static(patterns, options) {
        const entries = [];
        for await (const entry of this._readerStream.static(patterns, options)) {
            entries.push(entry);
        }
        return entries;
    }
}
