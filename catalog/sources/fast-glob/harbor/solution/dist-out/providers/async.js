import { Provider } from './provider.js';
export class ProviderAsync extends Provider {
    #reader;
    constructor(reader, settings) {
        super(settings);
        this.#reader = reader;
    }
    async read(task) {
        const root = this._getRootDirectory(task);
        const options = this._getReaderOptions(task);
        const entries = await this.api(root, task, options);
        return entries.map((entry) => options.transform(entry));
    }
    async api(root, task, options) {
        if (task.dynamic) {
            return this.#reader.dynamic(root, options);
        }
        return this.#reader.static(task.positive, options);
    }
}
