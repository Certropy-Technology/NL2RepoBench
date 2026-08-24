import type { ReaderAsyncInterface } from '../readers/index.js';
import type Settings from '../settings.js';
import type { Task } from '../managers/tasks.js';
import type { Entry, EntryItem, ReaderOptions } from '../types/index.js';
import { Provider } from './provider.js';
export declare class ProviderAsync extends Provider<Promise<EntryItem[]>> {
    #private;
    constructor(reader: ReaderAsyncInterface, settings: Settings);
    read(task: Task): Promise<EntryItem[]>;
    api(root: string, task: Task, options: ReaderOptions): Promise<Entry[]>;
}
