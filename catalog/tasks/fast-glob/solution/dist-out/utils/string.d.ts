export declare function isString(input: unknown): input is string;
export declare function isEmpty(input: string): boolean;
/**
 * Flattens the underlying C structures of a concatenated JavaScript string.
 *
 * More details: https://github.com/davidmarkclements/flatstr
 */
export declare function flatHeavilyConcatenatedString(input: string): string;
