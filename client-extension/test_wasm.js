const fs = require('fs');

(async () => {
    const wasmBuffer = fs.readFileSync('./src/wasm/entropy.wasm');
    const wasmModule = await WebAssembly.instantiate(wasmBuffer);
    const { calculate_entropy, memory } = wasmModule.instance.exports;

    const url = 'http://secure-login-update-account-73628.com';
    
    const encoder = new TextEncoder();
    const urlBytes = encoder.encode(url + '\0');
    
    // Write at arbitrary offset since no malloc is exported in this standalone build
    const offset = 1024;
    const view = new Uint8Array(memory.buffer, offset, urlBytes.length);
    view.set(urlBytes);

    const start = performance.now();
    const entropy = calculate_entropy(offset);
    const end = performance.now();

    console.log(`URL: ${url}`);
    console.log(`Entropy: ${entropy}`);
    console.log(`Execution Time: ${(end - start).toFixed(4)} ms`);
})();
