import { Router } from './router.js';
import { renderUI } from './ui.js';

class AetherApp {
    constructor() {
        this.router = new Router();
        this.init();
    }
    init() {
        console.log('⚡ [AETHER] Olympic-level runtime initialized on M4 Max.');
        renderUI();
    }
}

new AetherApp();