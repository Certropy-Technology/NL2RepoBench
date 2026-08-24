import * as path from 'node:path';
import * as utils from '../utils/index.js';
import DeepFilter from './filters/deep.js';
import EntryFilter from './filters/entry.js';
import ErrorFilter from './filters/error.js';
import EntryTransformer from './transformers/entry.js';
export class Provider {
    #settings;
    errorFilter;
    entryFilter;
    deepFilter;
    entryTransformer;
    constructor(settings) {
        this.#settings = settings;
        const micromatchOptions = this._getMicromatchOptions();
        this.errorFilter = new ErrorFilter(settings);
        this.entryFilter = new EntryFilter(settings, micromatchOptions);
        this.deepFilter = new DeepFilter(settings, micromatchOptions);
        this.entryTransformer = new EntryTransformer(settings);
    }
    _getRootDirectory(task) {
        const root = path.resolve(this.#settings.cwd, task.base);
        return utils.path.appendTrailingSeparatorToDeviceRoot(root);
    }
    _getReaderOptions(task) {
        const basePath = task.base === '.' ? '' : task.base;
        return {
            basePath,
            pathSegmentSeparator: '/',
            deepFilter: this.deepFilter.getFilter(basePath, task.positive, task.negative),
            entryFilter: this.entryFilter.getFilter(task.positive, task.negative),
            errorFilter: this.errorFilter.getFilter(),
            followSymbolicLinks: this.#settings.followSymbolicLinks,
            fs: this.#settings.fs,
            stats: this.#settings.stats,
            throwErrorOnBrokenSymbolicLink: this.#settings.throwErrorOnBrokenSymbolicLink,
            transform: this.entryTransformer.getTransformer(),
            signal: this.#settings.signal,
        };
    }
    _getMicromatchOptions() {
        return {
            dot: this.#settings.dot,
            matchBase: this.#settings.baseNameMatch,
            nobrace: !this.#settings.braceExpansion,
            nocase: !this.#settings.caseSensitiveMatch,
            noext: !this.#settings.extglob,
            noglobstar: !this.#settings.globstar,
            posix: true,
            strictSlashes: false,
        };
    }
}
