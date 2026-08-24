import * as fs from 'node:fs';
import * as process from 'node:process';
export const DEFAULT_FILE_SYSTEM_ADAPTER = {
    lstat: fs.lstat,
    lstatSync: fs.lstatSync,
    stat: fs.stat,
    statSync: fs.statSync,
    readdir: fs.readdir,
    readdirSync: fs.readdirSync,
};
export default class Settings {
    absolute;
    baseNameMatch;
    braceExpansion;
    caseSensitiveMatch;
    cwd;
    deep;
    dot;
    extglob;
    followSymbolicLinks;
    fs;
    globstar;
    ignore;
    markDirectories;
    objectMode;
    onlyDirectories;
    onlyFiles;
    stats;
    suppressErrors;
    throwErrorOnBrokenSymbolicLink;
    unique;
    signal;
    // eslint-disable-next-line complexity
    constructor(options = {}) {
        if (options.deep !== undefined && options.deep < 0) {
            throw new TypeError(`options.deep must be a non-negative number, received: ${options.deep}`);
        }
        this.absolute = options.absolute ?? false;
        this.baseNameMatch = options.baseNameMatch ?? false;
        this.braceExpansion = options.braceExpansion ?? true;
        this.caseSensitiveMatch = options.caseSensitiveMatch ?? true;
        this.cwd = options.cwd ?? process.cwd();
        this.deep = options.deep ?? Infinity;
        this.dot = options.dot ?? false;
        this.extglob = options.extglob ?? true;
        this.followSymbolicLinks = options.followSymbolicLinks ?? true;
        this.fs = this.#getFileSystemMethods(options.fs);
        this.globstar = options.globstar ?? true;
        this.ignore = options.ignore ?? [];
        this.markDirectories = options.markDirectories ?? false;
        this.objectMode = options.objectMode ?? false;
        this.onlyDirectories = options.onlyDirectories ?? false;
        this.onlyFiles = options.onlyFiles ?? true;
        this.stats = options.stats ?? false;
        this.suppressErrors = options.suppressErrors ?? false;
        this.throwErrorOnBrokenSymbolicLink = options.throwErrorOnBrokenSymbolicLink ?? false;
        this.unique = options.unique ?? true;
        this.signal = options.signal;
        if (this.onlyDirectories) {
            this.onlyFiles = false;
        }
        if (this.stats) {
            this.objectMode = true;
        }
    }
    #getFileSystemMethods(methods = {}) {
        return {
            ...DEFAULT_FILE_SYSTEM_ADAPTER,
            ...methods,
        };
    }
}
