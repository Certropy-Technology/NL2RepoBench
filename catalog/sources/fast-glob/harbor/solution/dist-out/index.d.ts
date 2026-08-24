import * as taskManager from './managers/tasks.js';
import { type Options as OptionsInternal } from './settings.js';
import type { Entry as EntryInternal, FileSystemAdapter as FileSystemAdapterInternal, Pattern as PatternInternal } from './types/index.js';
type InputPattern = PatternInternal | readonly PatternInternal[];
type EntryObjectModePredicate = {
    [TKey in keyof Pick<OptionsInternal, 'objectMode'>]-?: true;
};
type EntryStatsPredicate = {
    [TKey in keyof Pick<OptionsInternal, 'stats'>]-?: true;
};
type EntryObjectPredicate = EntryObjectModePredicate | EntryStatsPredicate;
export type Options = OptionsInternal;
export type Entry = EntryInternal;
export type Task = taskManager.Task;
export type Pattern = PatternInternal;
export type FileSystemAdapter = FileSystemAdapterInternal;
export declare function glob(source: InputPattern, options: EntryObjectPredicate & OptionsInternal): Promise<EntryInternal[]>;
export declare function glob(source: InputPattern, options?: OptionsInternal): Promise<string[]>;
/**
 * @deprecated
 * This method will be removed in v5, use the `.glob` method instead.
 */
export declare const async: typeof glob;
export declare function globSync(source: InputPattern, options: EntryObjectPredicate & OptionsInternal): EntryInternal[];
export declare function globSync(source: InputPattern, options?: OptionsInternal): string[];
/**
 * @deprecated
 * This method will be removed in v5, use the `.globSync` method instead.
 */
export declare const sync: typeof globSync;
export declare function globStream(source: InputPattern, options?: OptionsInternal): NodeJS.ReadableStream;
/**
 * @deprecated
 * This method will be removed in v5, use the `.globStream` method instead.
 */
export declare const stream: typeof globStream;
export declare function generateTasks(source: InputPattern, options?: OptionsInternal): Task[];
export declare function isDynamicPattern(source: PatternInternal, options?: OptionsInternal): boolean;
export declare const escapePath: (source: string) => string;
export declare const convertPathToPattern: (source: string) => string;
export declare const posix: {
    escapePath: (source: string) => string;
    convertPathToPattern: (source: string) => string;
};
export declare const win32: {
    escapePath: (source: string) => string;
    convertPathToPattern: (source: string) => string;
};
export {};
