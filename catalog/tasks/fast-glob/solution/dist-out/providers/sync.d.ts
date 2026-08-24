import type { ReaderSyncInterface } from '../readers/index.js';
import type Settings from '../settings.js';
import type { Task } from '../managers/tasks.js';
import type { Entry, EntryItem, ReaderOptions } from '../types/index.js';
import { Provider } from './provider.js';
export declare class ProviderSync extends Provider<EntryItem[]> {
    #private;
    constructor(reader: ReaderSyncInterface, settings: Settings);
    read(task: Task): EntryItem[];
    api(root: string, task: Task, options: ReaderOptions): Entry[];
}
