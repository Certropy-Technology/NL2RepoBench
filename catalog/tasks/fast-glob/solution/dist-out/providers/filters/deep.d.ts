import type { MicromatchOptions, EntryFilterFunction, Pattern } from '../../types/index.js';
import type Settings from '../../settings.js';
export default class DeepFilter {
    #private;
    constructor(settings: Settings, micromatchOptions: MicromatchOptions);
    getFilter(basePath: string, positive: Pattern[], negative: Pattern[]): EntryFilterFunction;
}
