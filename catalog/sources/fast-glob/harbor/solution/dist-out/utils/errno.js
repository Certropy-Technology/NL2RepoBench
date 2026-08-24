export function isEnoentCodeError(error) {
    return error.code === 'ENOENT';
}
