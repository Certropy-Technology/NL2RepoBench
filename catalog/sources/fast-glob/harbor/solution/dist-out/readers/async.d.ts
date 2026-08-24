import * as fsWalk from '@nodelib/fs.walk';
import type Settings from '../settings.js';
import type { Entry, ReaderOptions, Pattern } from '../types/index.js';
import { Reader } from './reader.js';
import { ReaderStream } from './stream.js';
export type ReaderAsyncInterface = {
    dynamic: (root: string, options: ReaderOptions) => Promise<Entry[]>;
    static: (patterns: Pattern[], options: ReaderOptions) => Promise<Entry[]>;
};
export declare class ReaderAsync extends Reader<Promise<Entry[]>> implements ReaderAsyncInterface {
    protected _walkAsync: typeof fsWalk.walk;
    protected _readerStream: ReaderStream;
    constructor(settings: Settings);
    dynamic(root: string, options: ReaderOptions): Promise<Entry[]>;
    static(patterns: Pattern[], options: ReaderOptions): Promise<Entry[]>;
}
