import * as fs from 'node:fs';
const _kStats = Symbol('stats');
// Adapting an internal class in Node.js to mimic the behavior of `fs.Dirent` when creating it manually from `fs.Stats`.
// https://github.com/nodejs/node/blob/a4cf6b204f0b160480153dc293ae748bf15225f9/lib/internal/fs/utils.js#L199C1-L213
export class DirentFromStats extends fs.Dirent {
    [_kStats];
    constructor(name, stats) {
        // @ts-expect-error The constructor has parameters, but they are not represented in types.
        // https://github.com/nodejs/node/blob/a4cf6b204f0b160480153dc293ae748bf15225f9/lib/internal/fs/utils.js#L164
        super(name, null);
        this[_kStats] = stats;
    }
}
for (const key of Reflect.ownKeys(fs.Dirent.prototype)) {
    const name = key;
    if (name === 'constructor') {
        continue;
    }
    DirentFromStats.prototype[name] = function () {
        return this[_kStats][name]();
    };
}
export function createDirentFromStats(name, stats) {
    return new DirentFromStats(name, stats);
}
