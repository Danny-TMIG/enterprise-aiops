export class Router {
    constructor() {
        this.routes = {};
    }
    register(path, callback) {
        this.routes[path] = callback;
    }
    navigate(path) {
        if (this.routes[path]) {
            this.routes[path]();
        }
    }
}
