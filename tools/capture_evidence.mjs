// Genera las capturas de evidencia ejecutando la app web real en Chrome.
// Uso: node tools/capture_evidence.mjs
// Requiere: flutter build web --release y un servidor estático en http://127.0.0.1:8081
import { spawn } from 'node:child_process';
import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import process from 'node:process';

const APP_URL = process.env.APP_URL ?? 'http://127.0.0.1:8081/';
const OUT_DIR = path.resolve('evidencias');
const PORT = 9333;
const CHROME =
  process.env.CHROME_PATH ?? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`HTTP ${response.status} al consultar ${url}`);
  return response.json();
}

mkdirSync(OUT_DIR, { recursive: true });
const profile = mkdtempSync(path.join(tmpdir(), 'pt-cubit-chrome-'));
const chrome = spawn(
  CHROME,
  [
    '--headless=new',
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${profile}`,
    '--window-size=1100,820',
    '--hide-scrollbars',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-extensions',
    'about:blank',
  ],
  { stdio: 'ignore' },
);

let browserWs;
try {
  let version;
  for (let i = 0; i < 50; i += 1) {
    try {
      version = await getJson(`http://127.0.0.1:${PORT}/json/version`);
      break;
    } catch {
      await delay(200);
    }
  }
  if (!version) throw new Error('Chrome no expuso el puerto de depuración');

  browserWs = new WebSocket(version.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    browserWs.onopen = resolve;
    browserWs.onerror = reject;
  });

  let nextId = 0;
  const pending = new Map();
  const listeners = new Set();

  browserWs.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
      return;
    }
    listeners.add && listeners.forEach((listener) => listener(msg));
  };

  const send = (method, params = {}, sessionId) =>
    new Promise((resolve, reject) => {
      const id = ++nextId;
      pending.set(id, { resolve, reject });
      browserWs.send(
        JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }),
      );
    });

  const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
  const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
  const cmd = (method, params = {}) => send(method, params, sessionId);

  await cmd('Page.enable');
  await cmd('Runtime.enable');
  await cmd('Accessibility.enable');
  await cmd('Fetch.enable', {
    patterns: [
      {
        urlPattern: '*jsonplaceholder.typicode.com/users*',
        requestStage: 'Request',
      },
    ],
  });
  await cmd('Emulation.setDeviceMetricsOverride', {
    width: 1100,
    height: 820,
    deviceScaleFactor: 1,
    mobile: false,
  });

  // Normal, vacío, error o lento: simula respuestas de la API sin cambiar el Cubit.
  let mode = 'normal';
  listeners.add((msg) => {
    if (msg.method !== 'Fetch.requestPaused' || msg.sessionId !== sessionId) return;
    const { requestId } = msg.params;
    const cors = [
      { name: 'access-control-allow-origin', value: '*' },
      { name: 'content-type', value: 'application/json' },
    ];

    if (mode === 'vacio') {
      void cmd('Fetch.fulfillRequest', {
        requestId,
        responseCode: 200,
        responseHeaders: cors,
        body: Buffer.from('[]').toString('base64'),
      }).catch(() => {});
    } else if (mode === 'error') {
      void cmd('Fetch.fulfillRequest', {
        requestId,
        responseCode: 500,
        responseHeaders: cors,
        body: Buffer.from('{"error":"server"}').toString('base64'),
      }).catch(() => {});
    } else if (mode === 'lento') {
      setTimeout(() => {
        void cmd('Fetch.continueRequest', { requestId }).catch(() => {});
      }, 3500);
    } else {
      void cmd('Fetch.continueRequest', { requestId }).catch(() => {});
    }
  });

  const evalJs = async (expression) => {
    const result = await cmd('Runtime.evaluate', {
      expression,
      returnByValue: true,
    });
    return result.result.value;
  };

  const waitForApp = async () => {
    for (let i = 0; i < 100; i += 1) {
      const ready = await evalJs(
        "!!document.querySelector('flt-glass-pane') || !!document.querySelector('canvas')",
      );
      if (ready) {
        await delay(800);
        // Activa la semántica de Flutter para poder leer el estado por accesibilidad.
        await evalJs(
          "document.querySelector('[aria-label=\"Enable accessibility\"]')?.click()",
        );
        await delay(600);
        return;
      }
      await delay(200);
    }
    throw new Error('La app Flutter no terminó de cargar');
  };

  const shot = async (name) => {
    const { data } = await cmd('Page.captureScreenshot', { format: 'png' });
    const file = path.join(OUT_DIR, name);
    writeFileSync(file, Buffer.from(data, 'base64'));
    const ax = await cmd('Accessibility.getFullAXTree');
    const labels = ax.nodes
      .map((node) => node.name?.value)
      .filter(Boolean)
      .join(' | ');
    console.log(`Guardada: ${file}\n  Accesibilidad: ${labels.slice(0, 500) || '(sin etiquetas)'}`);
  };

  const clickFab = async () => {
    // FAB extendido en la esquina inferior derecha (viewport 1100x820).
    for (const type of ['mousePressed', 'mouseReleased']) {
      await cmd('Input.dispatchMouseEvent', {
        type,
        x: 975,
        y: 760,
        button: 'left',
        clickCount: 1,
      });
    }
  };

  const openApp = async (nextMode) => {
    mode = nextMode;
    await cmd('Page.navigate', { url: APP_URL });
    await waitForApp();
  };

  await openApp('normal');
  await shot('figura_1_inicial.png');

  await openApp('lento');
  await clickFab();
  await delay(900);
  await shot('figura_2_carga.png');

  await openApp('normal');
  await clickFab();
  await delay(5000);
  await shot('figura_3_exito.png');

  await openApp('vacio');
  await clickFab();
  await delay(2500);
  await shot('figura_4_vacio.png');

  await openApp('error');
  await clickFab();
  await delay(2500);
  await shot('figura_5_error.png');

  console.log('Evidencias generadas en', OUT_DIR);
} finally {
  browserWs?.close();
  chrome.kill();
}
