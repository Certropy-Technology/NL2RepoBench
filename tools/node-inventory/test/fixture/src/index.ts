export type ParseOptions = { strict?: boolean };
export function parse(value: string, options: ParseOptions = {}): string {
  if (options.strict && !value) throw new TypeError("empty");
  return value.trim();
}
export class Reader {
  constructor(private readonly source: string) {}
  public async read(
    limit: number = 10,
    strict: boolean = false,
  ): Promise<string> {
    if (strict && limit < 0) throw new RangeError("limit");
    return this.source.slice(0, limit);
  }
}
export { parse as normalize };
import("./optional.js");
eval("void 0");
fetch("https://example.invalid");
import { createRequire } from "node:module";
import "bindings";
createRequire(import.meta.url)("bindings");
