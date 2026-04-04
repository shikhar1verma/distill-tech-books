/**
 * Mermaid diagram syntax validator.
 *
 * Reads JSON array of {file, line, content} from stdin.
 * Writes JSON array of {file, line, valid, error} to stdout.
 *
 * Usage:
 *   echo '[...]' | node src/validate-mermaid.mjs
 */

import { JSDOM } from "jsdom";

// Mermaid requires a DOM environment — set up before importing mermaid
const dom = new JSDOM("<!DOCTYPE html><html><body><div id='mermaid'></div></body></html>");
global.window = dom.window;
global.document = dom.window.document;
global.self = dom.window;

// navigator is a getter in Node 22+, use defineProperty
Object.defineProperty(global, "navigator", {
  value: dom.window.navigator,
  writable: true,
  configurable: true,
});

// Mock DOMPurify — mermaid v11+ requires it but jsdom doesn't provide it.
// For validation (parse-only), sanitization is not needed.
global.DOMPurify = {
  addHook: () => {},
  removeHook: () => {},
  removeHooks: () => {},
  removeAllHooks: () => {},
  sanitize: (html) => html,
  isSupported: true,
  setConfig: () => {},
};
global.window.DOMPurify = global.DOMPurify;

const { default: mermaid } = await import("mermaid");

mermaid.initialize({
  startOnLoad: false,
  suppressErrors: true,
  logLevel: "fatal",
  secure: [],         // disable security checks that need DOMPurify
});

// Read all stdin
const chunks = [];
for await (const chunk of process.stdin) {
  chunks.push(chunk);
}
const input = Buffer.concat(chunks).toString("utf-8");

let blocks;
try {
  blocks = JSON.parse(input);
} catch (e) {
  console.error(`Invalid JSON input: ${e.message}`);
  process.exit(1);
}

const results = [];

for (const block of blocks) {
  try {
    await mermaid.parse(block.content);
    results.push({ file: block.file, line: block.line, valid: true, error: null });
  } catch (e) {
    const msg = e.message || String(e);
    const cleaned = msg
      .replace(/\n/g, " ")
      .replace(/\s+/g, " ")
      .trim()
      .slice(0, 200);
    results.push({ file: block.file, line: block.line, valid: false, error: cleaned });
  }
}

console.log(JSON.stringify(results));
