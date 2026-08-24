import * as utils from '../../utils/index.js';
export default class ErrorFilter {
    #settings;
    constructor(settings) {
        this.#settings = settings;
    }
    #isNonFatalError(error) {
        return utils.errno.isEnoentCodeError(error) || this.#settings.suppressErrors;
    }
    getFilter() {
        return (error) => this.#isNonFatalError(error);
    }
}
