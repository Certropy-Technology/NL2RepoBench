import * as utils from '../../utils/index.js';
export default class Matcher {
    #patterns;
    #settings;
    #micromatchOptions;
    _storage = [];
    constructor(patterns, settings, micromatchOptions) {
        this.#patterns = patterns;
        this.#settings = settings;
        this.#micromatchOptions = micromatchOptions;
        this.#fillStorage();
    }
    #fillStorage() {
        for (const pattern of this.#patterns) {
            const segments = this.#getPatternSegments(pattern);
            const sections = this.#splitSegmentsIntoSections(segments);
            this._storage.push({
                complete: sections.length <= 1,
                pattern,
                segments,
                sections,
            });
        }
    }
    #getPatternSegments(pattern) {
        const parts = utils.pattern.getPatternParts(pattern, this.#micromatchOptions);
        return parts.map((part) => {
            const isDynamic = utils.pattern.isDynamicPattern(part, this.#settings);
            if (!isDynamic) {
                return {
                    dynamic: false,
                    pattern: part,
                };
            }
            return {
                dynamic: true,
                pattern: part,
                patternRe: utils.pattern.makeRe(part, this.#micromatchOptions),
            };
        });
    }
    #splitSegmentsIntoSections(segments) {
        return utils.array.splitWhen(segments, (segment) => segment.dynamic && utils.pattern.hasGlobStar(segment.pattern));
    }
}
