import type Settings from '../settings.js';
import type { MicromatchOptions, ReaderOptions } from '../types/index.js';
import type { Task } from '../managers/tasks.js';
import DeepFilter from './filters/deep.js';
import EntryFilter from './filters/entry.js';
import ErrorFilter from './filters/error.js';
import EntryTransformer from './transformers/entry.js';
export declare abstract class Provider<T> {
    #private;
    readonly errorFilter: ErrorFilter;
    readonly entryFilter: EntryFilter;
    readonly deepFilter: DeepFilter;
    readonly entryTransformer: EntryTransformer;
    constructor(settings: Settings);
    abstract read(_task: Task): T;
    protected _getRootDirectory(task: Task): string;
    protected _getReaderOptions(task: Task): ReaderOptions;
    protected _getMicromatchOptions(): MicromatchOptions;
}
