import * as utils from '../../utils/index.js';
import PartialMatcher from '../matchers/partial.js';
export default class DeepFilter {
    #settings;
    #micromatchOptions;
    constructor(settings, micromatchOptions) {
        this.#settings = settings;
        this.#micromatchOptions = micromatchOptions;
    }
    #getMatcher(patterns) {
        return new PartialMatcher(patterns, this.#settings, this.#micromatchOptions);
    }
    #getNegativePatternsRe(patterns) {
        const affectDepthOfReadingPatterns = patterns.filter((pattern) => utils.pattern.isAffectDepthOfReadingPattern(pattern));
        return utils.pattern.convertPatternsToRe(affectDepthOfReadingPatterns, this.#micromatchOptions);
    }
    #filter(basePath, entry, matcher, negativeRe) {
        if (this.#isSkippedByDeep(basePath, entry.path)) {
            return false;
        }
        if (this.#isSkippedSymbolicLink(entry)) {
            return false;
        }
        const filepath = utils.path.removeLeadingDotSegment(entry.path);
        if (this.#isSkippedByPositivePatterns(filepath, matcher)) {
            return false;
        }
        return this.#isSkippedByNegativePatterns(filepath, negativeRe);
    }
    #isSkippedByDeep(basePath, entryPath) {
        /**
         * Avoid unnecessary depth calculations when it doesn't matter.
         */
        if (this.#settings.deep === Infinity) {
            return false;
        }
        return this.#getEntryLevel(basePath, entryPath) >= this.#settings.deep;
    }
    #getEntryLevel(basePath, entryPath) {
        const entryPathDepth = entryPath.split('/').length;
        if (basePath === '') {
            return entryPathDepth;
        }
        const basePathDepth = basePath.split('/').length;
        return entryPathDepth - basePathDepth;
    }
    #isSkippedSymbolicLink(entry) {
        return !this.#settings.followSymbolicLinks && entry.dirent.isSymbolicLink();
    }
    #isSkippedByPositivePatterns(entryPath, matcher) {
        return !this.#settings.baseNameMatch && !matcher.match(entryPath);
    }
    #isSkippedByNegativePatterns(entryPath, patternsRe) {
        return !utils.pattern.isMatchAny(entryPath, patternsRe);
    }
    getFilter(basePath, positive, negative) {
        const matcher = this.#getMatcher(positive);
        const negativeRe = this.#getNegativePatternsRe(negative);
        return (entry) => this.#filter(basePath, entry, matcher, negativeRe);
    }
}
