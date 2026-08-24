export function flatFirstLevel(items) {
    // We do not use `Array.flat` because this is slower than current implementation for your case.
    // eslint-disable-next-line unicorn/prefer-spread
    return [].concat(...items);
}
export function splitWhen(items, isNextGroup) {
    const result = [[]];
    let groupIndex = 0;
    for (const item of items) {
        if (isNextGroup(item)) {
            groupIndex++;
            result[groupIndex] = [];
        }
        else {
            result[groupIndex].push(item);
        }
    }
    return result;
}
