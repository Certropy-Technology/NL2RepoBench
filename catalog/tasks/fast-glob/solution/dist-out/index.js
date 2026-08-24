import * as taskManager from './managers/tasks.js';
import Settings, {} from './settings.js';
import * as utils from './utils/index.js';
import { ProviderAsync, ProviderStream, ProviderSync } from './providers/index.js';
import { ReaderAsync, ReaderStream, ReaderSync } from './readers/index.js';
export async function glob(source, options) {
    assertPatternsInput(source);
    const settings = new Settings(options);
    const reader = new ReaderAsync(settings);
    const provider = new ProviderAsync(reader, settings);
    const tasks = getTasks(source, settings);
    const promises = tasks.map(async (task) => provider.read(task));
    const result = await Promise.all(promises);
    return utils.array.flatFirstLevel(result);
}
/**
 * @deprecated
 * This method will be removed in v5, use the `.glob` method instead.
 */
export const async = glob;
export function globSync(source, options) {
    assertPatternsInput(source);
    const settings = new Settings(options);
    const reader = new ReaderSync(settings);
    const provider = new ProviderSync(reader, settings);
    const tasks = getTasks(source, settings);
    const entries = tasks.map((task) => provider.read(task));
    return utils.array.flatFirstLevel(entries);
}
/**
 * @deprecated
 * This method will be removed in v5, use the `.globSync` method instead.
 */
export const sync = globSync;
export function globStream(source, options) {
    assertPatternsInput(source);
    const settings = new Settings(options);
    const reader = new ReaderStream(settings);
    const provider = new ProviderStream(reader, settings);
    const tasks = getTasks(source, settings);
    const streams = tasks.map((task) => provider.read(task));
    /**
     * The stream returned by the provider cannot work with an asynchronous iterator.
     * To support asynchronous iterators, regardless of the number of tasks, we always multiplex streams.
     * This affects performance (+25%). I don't see best solution right now.
     */
    return utils.stream.merge(streams);
}
/**
 * @deprecated
 * This method will be removed in v5, use the `.globStream` method instead.
 */
export const stream = globStream;
export function generateTasks(source, options) {
    assertPatternsInput(source);
    const patterns = Array.isArray(source) ? source : [source];
    const settings = new Settings(options);
    return taskManager.generate(patterns, settings);
}
export function isDynamicPattern(source, options) {
    assertPatternsInput(source);
    const settings = new Settings(options);
    return utils.pattern.isDynamicPattern(source, settings);
}
export const escapePath = withPatternsInputAssert(utils.path.escape);
export const convertPathToPattern = withPatternsInputAssert(utils.path.convertPathToPattern);
export const posix = {
    escapePath: withPatternsInputAssert(utils.path.escapePosixPath),
    convertPathToPattern: withPatternsInputAssert(utils.path.convertPosixPathToPattern),
};
export const win32 = {
    escapePath: withPatternsInputAssert(utils.path.escapeWindowsPath),
    convertPathToPattern: withPatternsInputAssert(utils.path.convertWindowsPathToPattern),
};
function getTasks(source, settings) {
    const patterns = Array.isArray(source) ? source : [source];
    return taskManager.generate(patterns, settings);
}
function assertPatternsInput(input) {
    const source = Array.isArray(input) ? input : [input];
    const isValidSource = source.every((item) => utils.string.isString(item) && !utils.string.isEmpty(item));
    if (!isValidSource) {
        throw new TypeError('Patterns must be a string (non empty) or an array of strings');
    }
}
function withPatternsInputAssert(method) {
    return (source) => {
        assertPatternsInput(source);
        return method(source);
    };
}
