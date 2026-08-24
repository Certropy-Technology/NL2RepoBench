import * as utils from '../../utils/index.js';
export default class EntryFilter {
    #settings;
    #micromatchOptions;
    index = new Map();
    constructor(settings, micromatchOptions) {
        this.#settings = settings;
        this.#micromatchOptions = micromatchOptions;
    }
    #filter(entry, pattens) {
        const filepath = utils.path.removeLeadingDotSegment(entry.path);
        if (this.#settings.unique && this.#isDuplicateEntry(filepath)) {
            return false;
        }
        const isDirectory = entry.dirent.isDirectory();
        if (this.#onlyFileFilter(isDirectory) || this.#onlyDirectoryFilter(isDirectory)) {
            return false;
        }
        const isMatched = this.#isMatchToPatternsSet(filepath, pattens, isDirectory);
        if (this.#settings.unique && isMatched) {
            this.#createIndexRecord(filepath);
        }
        return isMatched;
    }
    #isDuplicateEntry(filepath) {
        return this.index.has(filepath);
    }
    #createIndexRecord(filepath) {
        this.index.set(filepath, undefined);
    }
    #onlyFileFilter(isDirectory) {
        return this.#settings.onlyFiles && isDirectory;
    }
    #onlyDirectoryFilter(isDirectory) {
        return this.#settings.onlyDirectories && !isDirectory;
    }
    #isMatchToPatternsSet(filepath, patterns, isDirectory) {
        const isMatched = this.#isMatchToPatterns(filepath, patterns.positive.all, isDirectory);
        if (!isMatched) {
            return false;
        }
        const isMatchedByRelativeNegative = this.#isMatchToPatterns(filepath, patterns.negative.relative, isDirectory);
        if (isMatchedByRelativeNegative) {
            return false;
        }
        const isMatchedByAbsoluteNegative = this.#isMatchToAbsoluteNegative(filepath, patterns.negative.absolute, isDirectory);
        return !isMatchedByAbsoluteNegative;
    }
    #isMatchToAbsoluteNegative(filepath, patternsRe, isDirectory) {
        if (patternsRe.length === 0) {
            return false;
        }
        const fullpath = utils.path.makeAbsolute(this.#settings.cwd, filepath);
        return this.#isMatchToPatterns(fullpath, patternsRe, isDirectory);
    }
    #isMatchToPatterns(filepath, patternsRe, isDirectory) {
        if (patternsRe.length === 0) {
            return false;
        }
        // Trying to match files and directories by patterns.
        const isMatched = utils.pattern.isMatchAny(filepath, patternsRe);
        // A pattern with a trailling slash can be used for directory matching.
        // To apply such pattern, we need to add a tralling slash to the path.
        if (!isMatched && isDirectory) {
            return utils.pattern.isMatchAny(`${filepath}/`, patternsRe);
        }
        return isMatched;
    }
    getFilter(positive, negative) {
        const [absoluteNegative, relativeNegative] = utils.pattern.partitionAbsoluteAndRelative(negative);
        const patterns = {
            positive: {
                all: utils.pattern.convertPatternsToRe(positive, this.#micromatchOptions),
            },
            negative: {
                absolute: utils.pattern.convertPatternsToRe(absoluteNegative, { ...this.#micromatchOptions, dot: true }),
                relative: utils.pattern.convertPatternsToRe(relativeNegative, { ...this.#micromatchOptions, dot: true }),
            },
        };
        return (entry) => this.#filter(entry, patterns);
    }
}
