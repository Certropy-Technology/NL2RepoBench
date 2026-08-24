import { type Readable } from 'node:stream';
import * as fsStat from '@nodelib/fs.stat';
import * as fsWalk from '@nodelib/fs.walk';
import type { Pattern, ReaderOptions } from '../types/index.js';
import { Reader } from './reader.js';
export type ReaderStreamInterface = {
    dynamic: (root: string, options: ReaderOptions) => Readable;
    static: (patterns: Pattern[], options: ReaderOptions) => Readable;
};
export declare class ReaderStream extends Reader<Readable> implements ReaderStreamInterface {
    #private;
    protected _walkStream: typeof fsWalk.walkStream;
    protected _stat: typeof fsStat.stat;
    dynamic(root: string, options: ReaderOptions): Readable;
    static(patterns: Pattern[], options: ReaderOptions): Readable;
}
