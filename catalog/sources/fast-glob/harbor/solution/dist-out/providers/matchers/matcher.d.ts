import type { MicromatchOptions, Pattern, PatternRe } from '../../types/index.js';
import type Settings from '../../settings.js';
export type PatternSegment = DynamicPatternSegment | StaticPatternSegment;
type StaticPatternSegment = {
    dynamic: false;
    pattern: Pattern;
};
type DynamicPatternSegment = {
    dynamic: true;
    pattern: Pattern;
    patternRe: PatternRe;
};
export type PatternSection = PatternSegment[];
export type PatternInfo = {
    /**
     * Indicates that the pattern has a globstar (more than a single section).
     */
    complete: boolean;
    pattern: Pattern;
    segments: PatternSegment[];
    sections: PatternSection[];
};
export default abstract class Matcher {
    #private;
    protected readonly _storage: PatternInfo[];
    constructor(patterns: Pattern[], settings: Settings, micromatchOptions: MicromatchOptions);
}
export {};
