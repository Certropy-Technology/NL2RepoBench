import type Settings from '../../settings.js';
import type { EntryTransformerFunction } from '../../types/index.js';
export default class EntryTransformer {
    #private;
    constructor(settings: Settings);
    getTransformer(): EntryTransformerFunction;
}
