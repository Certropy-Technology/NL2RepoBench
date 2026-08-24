import type Settings from '../../settings.js';
import type { MicromatchOptions, EntryFilterFunction, Pattern } from '../../types/index.js';
export default class EntryFilter {
    #private;
    readonly index: Map<string, undefined>;
    constructor(settings: Settings, micromatchOptions: MicromatchOptions);
    getFilter(positive: Pattern[], negative: Pattern[]): EntryFilterFunction;
}
