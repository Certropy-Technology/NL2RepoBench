import { Readable } from 'node:stream';
import type { ReaderStreamInterface } from '../readers/index.js';
import type Settings from '../settings.js';
import type { Task } from '../managers/tasks.js';
import type { ReaderOptions } from '../types/index.js';
import { Provider } from './provider.js';
export declare class ProviderStream extends Provider<Readable> {
    #private;
    constructor(reader: ReaderStreamInterface, settings: Settings);
    read(task: Task): Readable;
    api(root: string, task: Task, options: ReaderOptions): Readable;
}
