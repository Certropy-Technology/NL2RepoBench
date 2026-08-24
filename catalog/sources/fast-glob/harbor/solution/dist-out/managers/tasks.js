import * as utils from '../utils/index.js';
export function generate(input, settings) {
    const patterns = processPatterns([...input], settings);
    const ignore = processPatterns([...settings.ignore], settings);
    const positivePatterns = getPositivePatterns(patterns);
    const negativePatterns = getNegativePatternsAsPositive(patterns, ignore);
    const staticPatterns = positivePatterns.filter((pattern) => utils.pattern.isStaticPattern(pattern, settings));
    const dynamicPatterns = positivePatterns.filter((pattern) => utils.pattern.isDynamicPattern(pattern, settings));
    const staticTasks = convertPatternsToTasks(staticPatterns, negativePatterns, /* dynamic */ false);
    const dynamicTasks = convertPatternsToTasks(dynamicPatterns, negativePatterns, /* dynamic */ true);
    return [...staticTasks, ...dynamicTasks];
}
function processPatterns(input, settings) {
    let patterns = input;
    /**
     * The original pattern like `{,*,**,a/*}` can lead to problems checking the depth when matching entry
     * and some problems with the micromatch package (see fast-glob issues: #365, #394).
     *
     * To solve this problem, we expand all patterns containing brace expansion. This can lead to a slight slowdown
     * in matching in the case of a large set of patterns after expansion.
     */
    if (settings.braceExpansion) {
        patterns = utils.pattern.expandPatternsWithBraceExpansion(patterns);
    }
    /**
     * If the `baseNameMatch` option is enabled, we must add globstar to patterns, so that they can be used
     * at any nesting level.
     *
     * We do this here, because otherwise we have to complicate the filtering logic. For example, we need to change
     * the pattern in the filter before creating a regular expression. There is no need to change the patterns
     * in the application. Only on the input.
     */
    if (settings.baseNameMatch) {
        patterns = patterns.map((pattern) => pattern.includes('/') ? pattern : `**/${pattern}`);
    }
    /**
     * This method also removes duplicate slashes that may have been in the pattern or formed as a result of expansion.
     */
    return patterns.map((pattern) => utils.pattern.removeDuplicateSlashes(pattern));
}
/**
 * Returns tasks grouped by basic pattern directories.
 *
 * Patterns that can be found inside (`./`) and outside (`../`) the current directory are handled separately.
 * This is necessary because directory traversal starts at the base directory and goes deeper.
 */
export function convertPatternsToTasks(positive, negative, isDynamic) {
    const tasks = [];
    const patternsOutsideCurrentDirectory = utils.pattern.getPatternsOutsideCurrentDirectory(positive);
    const patternsInsideCurrentDirectory = utils.pattern.getPatternsInsideCurrentDirectory(positive);
    const outsideCurrentDirectoryGroup = groupPatternsByBaseDirectory(patternsOutsideCurrentDirectory);
    const insideCurrentDirectoryGroup = groupPatternsByBaseDirectory(patternsInsideCurrentDirectory);
    tasks.push(...convertPatternGroupsToTasks(outsideCurrentDirectoryGroup, negative, isDynamic));
    /*
     * For the sake of reducing future accesses to the file system, we merge all tasks within the current directory
     * into a global task, if at least one pattern refers to the root (`.`). In this case, the global task covers the rest.
     *
     * Absolute patterns must not participate in this merge, because their base directory is independent of the current
     * directory. Otherwise, entries found by traversing the current directory will be matched against the absolute
     * pattern without the path prefix and never match.
     */
    if (Object.hasOwn(insideCurrentDirectoryGroup, '.')) {
        const [absolutePatterns, relativePatterns] = utils.pattern.partitionAbsoluteAndRelative(patternsInsideCurrentDirectory);
        if (absolutePatterns.length > 0) {
            tasks.push(...convertPatternGroupsToTasks(groupPatternsByBaseDirectory(absolutePatterns), negative, isDynamic));
        }
        tasks.push(convertPatternGroupToTask('.', relativePatterns, negative, isDynamic));
    }
    else {
        tasks.push(...convertPatternGroupsToTasks(insideCurrentDirectoryGroup, negative, isDynamic));
    }
    return tasks;
}
export function getPositivePatterns(patterns) {
    return utils.pattern.getPositivePatterns(patterns);
}
export function getNegativePatternsAsPositive(patterns, ignore) {
    const negative = [...utils.pattern.getNegativePatterns(patterns), ...ignore];
    const positive = negative.map((pattern) => utils.pattern.convertToPositivePattern(pattern));
    return positive;
}
export function groupPatternsByBaseDirectory(patterns) {
    const group = {};
    for (const pattern of patterns) {
        let base = utils.pattern.getBaseDirectory(pattern);
        /**
         * After extracting the basic static part of the pattern, it becomes a path,
         * so escaping leads to referencing non-existent paths.
         */
        base = utils.path.removeBackslashes(base);
        if (Object.hasOwn(group, base)) {
            group[base].push(pattern);
        }
        else {
            group[base] = [pattern];
        }
    }
    return group;
}
export function convertPatternGroupsToTasks(positive, negative, isDynamic) {
    return Object.entries(positive).map(([base, value]) => convertPatternGroupToTask(base, value, negative, isDynamic));
}
export function convertPatternGroupToTask(base, positive, negative, isDynamic) {
    return {
        dynamic: isDynamic,
        positive,
        negative,
        base,
        patterns: [...positive, ...negative.map((pattern) => utils.pattern.convertToNegativePattern(pattern))],
    };
}
