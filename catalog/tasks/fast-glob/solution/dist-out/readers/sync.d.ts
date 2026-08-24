import * as fsStat from '@nodelib/fs.stat';
import * as fsWalk from '@nodelib/fs.walk';
import type { Entry, Pattern, ReaderOptions } from '../types/index.js';
import { Reader } from './reader.js';
export type ReaderSyncInterface = {
    dynamic: (root: string, options: ReaderOptions) => Entry[];
    static: (patterns: Pattern[], options: ReaderOptions) => Entry[];
};
export declare class ReaderSync extends Reader<Entry[]> implements ReaderSyncInterface {
    #private;
    protected _walkSync: typeof fsWalk.walkSync;
    protected _statSync: typeof fsStat.statSync;
    dynamic(root: string, options: ReaderOptions): Entry[];
    static(patterns: Pattern[], options: ReaderOptions): Entry[];
}
