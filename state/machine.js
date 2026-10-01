class EnterpriseStateMachine {
    constructor() {
        this.state = "INTENT_CAPTURED";
        this.locked = false;
    }

    acquireLock(nodeId) {
        if (this.locked) {
            throw new Error(`Lock already acquired for node: ${nodeId}`);
        }
        this.locked = true;
        this.state = "ROUTED";
    }

    releaseLock() {
        this.locked = false;
        this.state = "COMMITTED";
    }

    transition(newState) {
        this.state = newState;
    }
}

module.exports = { EnterpriseStateMachine };
