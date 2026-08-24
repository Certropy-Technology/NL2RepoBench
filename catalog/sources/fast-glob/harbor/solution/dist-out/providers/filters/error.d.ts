import type Settings from '../../settings.js';
import type { ErrorFilterFunction } from '../../types/index.js';
export default class ErrorFilter {
    #private;
    constructor(settings: Settings);
    getFilter(): ErrorFilterFunction;
}
