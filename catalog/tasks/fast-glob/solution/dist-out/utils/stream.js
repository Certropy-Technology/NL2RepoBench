import merge2 from 'merge2';
export function merge(streams) {
    const mergedStream = merge2(streams);
    for (const stream of streams) {
        stream.once('error', (error) => {
            mergedStream.emit('error', error);
        });
    }
    mergedStream.once('close', () => {
        propagateCloseEventToSources(streams);
    });
    mergedStream.once('end', () => {
        propagateCloseEventToSources(streams);
    });
    return mergedStream;
}
function propagateCloseEventToSources(streams) {
    for (const stream of streams) {
        stream.emit('close');
    }
}
