self.onmessage = function(e) {
    const payload = e.data;
    console.log('[TENSOR WORKER] Processing local MLX stream:', payload);
    postMessage({ status: 'completed', node: 'apple-m4-max', timestamp: Date.now() });
};