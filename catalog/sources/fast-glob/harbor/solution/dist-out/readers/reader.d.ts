import * as fsStat from '@nodelib/fs.stat';
import type Settings from '../settings.js';
import type { Entry, ErrnoException, FsStats, Pattern, ReaderOptions } from '../types/index.js';
export declare abstract class Reader<T> {
    #private;
    protected readonly _fsStatSettings: fsStat.Settings;
    constructor(settings: Settings);
    abstract dynamic(root: string, options: ReaderOptions): T;
    abstract static(patterns: Pattern[], options: ReaderOptions): T;
    protected _getFullEntryPath(filepath: string): string;
    protected _makeEntry(stats: FsStats, pattern: Pattern): Entry;
    protected _isFatalError(error: ErrnoException): boolean;
}
