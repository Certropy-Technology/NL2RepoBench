import * as fs from 'node:fs';
import type { FsStats, FsDirent } from '../types/index.js';
declare const _kStats: unique symbol;
export declare class DirentFromStats extends fs.Dirent {
    private readonly [_kStats];
    constructor(name: string, stats: FsStats);
}
export declare function createDirentFromStats(name: string, stats: FsStats): FsDirent;
export {};
