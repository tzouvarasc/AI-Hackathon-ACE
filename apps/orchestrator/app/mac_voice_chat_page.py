from __future__ import annotations


def build_mac_voice_chat_html(*, server_stt_enabled: bool) -> str:
    return """<!doctype html>
<html lang=\"el\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Thalpo Voice Chat (Greek)</title>
    <link rel=\"stylesheet\" href=\"https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Source+Sans+3:wght@400;600;700&display=swap\" />
    <style>
      :root {
        --bg:         #f5e8c4;
        --bg-soft:    #e8d49a;
        --panel:      #fffef8;
        --panel-soft: #fdf8ec;
        --line:       rgba(60,30,10,0.10);
        --line-warm:  rgba(140,26,26,0.18);
        --text:       #261a0e;
        --text-mid:   #5c4d3c;
        --text-muted: #9a8c7c;
        --brand-red:  #8c1a1a;
        --amber:      #c47c3e;
        --amber-soft: rgba(196,124,62,0.12);
        --green:      #4e8c6e;
        --shadow:     0 4px 24px rgba(38,26,14,0.09);
        --shadow-md:  0 8px 32px rgba(38,26,14,0.13);
        --radius:     18px;
        --radius-md:  12px;
        --radius-sm:  9px;
      }
      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
      body {
        font-family: 'Source Sans 3', system-ui, sans-serif;
        font-size: 15px; line-height: 1.6;
        color: var(--text);
        background: var(--bg);
        min-height: 100vh;
        padding: 28px 16px 64px;
      }
      h1, h2, h3 { font-family: 'Playfair Display', Georgia, serif; }

      .wrap { max-width: 720px; margin: 0 auto; display: grid; gap: 14px; }

      /* ── Header ── */
      .thalpo-header {
        display: flex; align-items: center; gap: 16px;
        background: var(--panel); border: 1px solid var(--line);
        border-radius: var(--radius); box-shadow: var(--shadow);
        padding: 20px 24px;
      }
      .thalpo-logo-wrap {
        width: 54px; height: 54px; border-radius: 50%; flex-shrink: 0;
        background: url('/v1/logo.png') center/140% no-repeat;
        box-shadow: 0 4px 14px rgba(140,26,26,0.30);
      }
      .thalpo-header h1 { font-size: 1.6rem; color: var(--brand-red); margin-bottom: 2px; }
      .thalpo-header p  { font-size: 13.5px; color: var(--text-muted); }

      /* ── Status bar ── */
      .status-bar {
        display: flex; align-items: center; gap: 9px;
        background: var(--panel); border: 1px solid var(--line);
        border-radius: var(--radius-sm); padding: 10px 16px;
        font-size: 13.5px; color: var(--text-muted);
      }
      .status-dot {
        width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
        background: var(--text-muted);
      }

      /* ── Controls ── */
      .controls-card {
        background: var(--panel); border: 1px solid var(--line);
        border-radius: var(--radius); box-shadow: var(--shadow);
        padding: 22px 24px; display: grid; gap: 13px;
      }
      .call-row { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }
      .text-row  { display: flex; gap: 8px; }

      button {
        font-family: 'Source Sans 3', sans-serif;
        font-weight: 700; font-size: 14px;
        border: none; border-radius: var(--radius-sm);
        padding: 11px 20px; cursor: pointer;
        transition: opacity 0.15s, transform 0.1s;
        line-height: 1;
      }
      button:hover:not(:disabled) { opacity: 0.86; transform: translateY(-1px); }
      button:active:not(:disabled) { transform: none; }
      button:disabled { opacity: 0.38; cursor: not-allowed; transform: none; }

      #startMic {
        background: linear-gradient(135deg, var(--brand-red), #6b1414);
        color: #fff; padding: 13px 28px; font-size: 15px;
        box-shadow: 0 3px 14px rgba(140,26,26,0.26);
      }
      #stopMic {
        background: var(--amber-soft);
        border: 1.5px solid var(--line-warm);
        color: var(--brand-red);
      }
      #newSession {
        background: transparent;
        border: 1.5px solid var(--line);
        color: var(--text-muted);
      }
      #sendText {
        background: linear-gradient(135deg, var(--amber), #a06028);
        color: #fff;
        box-shadow: 0 2px 10px rgba(196,124,62,0.22);
        padding: 11px 20px; white-space: nowrap;
      }

      input[type=\"text\"] {
        flex: 1; min-width: 0;
        background: var(--panel-soft);
        border: 1px solid var(--line);
        border-radius: var(--radius-sm);
        padding: 11px 14px;
        font-family: inherit; font-size: 14.5px; color: var(--text);
        transition: border-color 0.2s, box-shadow 0.2s;
      }
      input[type=\"text\"]:focus {
        outline: none;
        border-color: var(--amber);
        box-shadow: 0 0 0 3px rgba(196,124,62,0.14);
      }
      input[type=\"text\"]::placeholder { color: var(--text-muted); }

      /* ── Conversation log ── */
      .log-card {
        background: var(--panel); border: 1px solid var(--line);
        border-radius: var(--radius); box-shadow: var(--shadow);
        overflow: hidden;
      }
      .log-label {
        padding: 12px 20px 10px;
        font-size: 10.5px; font-weight: 700; letter-spacing: 0.09em;
        text-transform: uppercase; color: var(--text-muted);
        border-bottom: 1px solid var(--line);
      }
      #log {
        padding: 14px 16px;
        min-height: 320px; max-height: 52vh;
        overflow-y: auto;
        display: grid; gap: 8px; align-content: start;
        background: var(--panel-soft);
      }
      .msg {
        padding: 11px 14px; border-radius: var(--radius-sm);
        font-size: 14px; line-height: 1.6;
      }
      .msg.user {
        background: rgba(196,124,62,0.10);
        border-left: 3px solid var(--amber);
      }
      .msg.bot {
        background: rgba(140,26,26,0.06);
        border-left: 3px solid var(--brand-red);
      }
      .msg.system {
        background: rgba(78,140,110,0.08);
        color: #2f5f46; font-size: 13px; font-style: italic;
        border-left: 3px solid var(--green);
      }
      .label { font-weight: 700; margin-right: 6px; }
      .msg.user .label { color: var(--amber); }
      .msg.bot  .label { color: var(--brand-red); }

      /* ── Footer note ── */
      .warn {
        text-align: center; font-size: 12.5px;
        color: var(--text-muted); font-style: italic;
        padding: 4px 0;
      }
    </style>
  </head>
  <body>
    <div class=\"wrap\">

      <div class=\"thalpo-header\">
        <div class=\"thalpo-logo-wrap\" role=\"img\" aria-label=\"Thalpo\"></div>
        <div>
          <h1>Thalpo</h1>
          <p>Φωνητική συνομιλία · Ελληνικά</p>
        </div>
      </div>

      <div class=\"status-bar\">
        <span class=\"status-dot\"></span>
        <span id=\"meta\">Κατάσταση: αρχικοποίηση…</span>
      </div>

      <div class=\"controls-card\">
        <div class=\"call-row\">
          <button id=\"startMic\">📞 Έναρξη κλήσης</button>
          <button id=\"stopMic\">Τερματισμός κλήσης</button>
          <button id=\"newSession\">Νέα συνεδρία</button>
        </div>
        <div class=\"text-row\">
          <input id=\"textInput\" type=\"text\" placeholder=\"Ή γράψτε εδώ και πατήστε Enter…\" />
          <button id=\"sendText\">Αποστολή</button>
        </div>
      </div>

      <div class=\"log-card\">
        <div class=\"log-label\">Συνομιλία</div>
        <div id=\"log\" class=\"log\"></div>
      </div>

      <p class=\"warn\">Browser STT (Safari/Chrome) · Server STT ενεργοποιείται αυτόματα αν είναι ρυθμισμένος.</p>

    </div>

    <script>
      const SERVER_STT_ENABLED = __SERVER_STT_ENABLED__;
      const meta = document.getElementById('meta');
      const log = document.getElementById('log');
      const textInput = document.getElementById('textInput');
      const startMicBtn = document.getElementById('startMic');
      const stopMicBtn = document.getElementById('stopMic');
      const newSessionBtn = document.getElementById('newSession');
      const sendTextBtn = document.getElementById('sendText');
      const CALL_OPENING_GREETING = 'Γεια σας! Είμαι η Θάλπω. Θα σας παίρνω τηλέφωνο κάθε μέρα για να τα λέμε λίγο. Πώς σας λένε;';

      let sessionId = null;
      let mediaRecorder = null;
      let mediaStream = null;
      let recordedChunks = [];
      let isRecording = false;
      let recognition = null;
      let isBrowserListening = false;
      let callModeActive = false;
      let pauseRecognitionForAudio = false;
      let currentAudio = null;
      let pendingTurns = [];
      let processingTurns = false;
      let lastTranscriptNorm = '';
      let lastTranscriptTs = 0;
      let cycleFinalTranscript = '';
      let cycleInterimTranscript = '';
      let callStartedAt = 0;
      let silenceHintTimer = null;
      let silenceHints = 0;
      let serverChunkMode = false;
      let serverChunkAbort = false;
      let serverSttDisabled = false;
      let noServerSttNoticeShown = false;
      let noTranscriptCycles = 0;
      let restartSttTimer = null;
      let silenceHintLogTs = 0;
      let lastAssistantNorm = '';
      let lastAssistantTs = 0;
      const MIN_RESTART_DELAY_MS = 400;
      const MAX_RESTART_DELAY_MS = 1800;
      const SILENCE_HINT_INTERVAL_MS = 7000;
      const AUTO_SWITCH_TO_SERVER_STT = false;

      function serverSttUsable() {
        return SERVER_STT_ENABLED && !serverSttDisabled;
      }

      function setMeta(message) {
        meta.textContent = message;
      }

      function addMessage(kind, label, text) {
        const block = document.createElement('div');
        block.className = `msg ${kind}`;

        const labelEl = document.createElement('span');
        labelEl.className = 'label';
        labelEl.textContent = label;

        const textEl = document.createElement('span');
        textEl.textContent = text;

        block.appendChild(labelEl);
        block.appendChild(textEl);
        log.appendChild(block);
        log.scrollTop = log.scrollHeight;
      }

      function nowTime() {
        try {
          return new Date().toLocaleTimeString('el-GR', { hour12: false });
        } catch (_) {
          return new Date().toISOString().slice(11, 19);
        }
      }

      function addStage(text) {
        addMessage('system', `[${nowTime()}]`, text);
      }

      function clearSilenceHintTimer() {
        if (silenceHintTimer) {
          window.clearTimeout(silenceHintTimer);
          silenceHintTimer = null;
        }
      }

      function armSilenceHintTimer() {
        clearSilenceHintTimer();
        if (!callModeActive) return;

        silenceHintTimer = window.setTimeout(() => {
          if (!callModeActive) return;

          const browserBusy =
            pauseRecognitionForAudio ||
            processingTurns ||
            pendingTurns.length > 0 ||
            serverChunkMode ||
            !isBrowserListening;

          if (browserBusy) {
            armSilenceHintTimer();
            return;
          }

          silenceHints += 1;
          const now = Date.now();
          if (now - silenceHintLogTs >= SILENCE_HINT_INTERVAL_MS - 1000) {
            addStage('Δεν άκουσα ακόμη καθαρό turn. Μιλήστε λίγο πιο αργά και καθαρά.');
            silenceHintLogTs = now;
          }

          if (silenceHints >= 2 && !serverSttUsable() && !noServerSttNoticeShown) {
            addStage('Server STT δεν είναι διαθέσιμο. Ελέγξτε μικρόφωνο Safari ή δοκιμάστε Chrome.');
            noServerSttNoticeShown = true;
          }

          const browserHasCandidate =
            Boolean(cycleFinalTranscript.trim()) ||
            Boolean(cycleInterimTranscript.trim()) ||
            pendingTurns.length > 0 ||
            processingTurns;

          if (
            AUTO_SWITCH_TO_SERVER_STT &&
            silenceHints >= 3 &&
            serverSttUsable() &&
            !serverChunkMode &&
            !browserHasCandidate
          ) {
            addStage('Auto-switch σε server STT mode γιατί ο browser STT δεν έδωσε transcript.');
            if (recognition && isBrowserListening) {
              try {
                recognition.stop();
              } catch (_) {
                // no-op
              }
            }
            startServerChunkMode().catch((err) => {
              addMessage('system', 'System:', `Σφάλμα server STT mode: ${err.message || err}`);
            });
            return;
          }

          armSilenceHintTimer();
        }, SILENCE_HINT_INTERVAL_MS);
      }

      async function sleepMs(ms) {
        return await new Promise((resolve) => window.setTimeout(resolve, ms));
      }

      function clearRestartTimer() {
        if (restartSttTimer) {
          window.clearTimeout(restartSttTimer);
          restartSttTimer = null;
        }
      }

      function scheduleBrowserRestart(delayMs) {
        clearRestartTimer();
        restartSttTimer = window.setTimeout(() => {
          restartSttTimer = null;
          if (!callModeActive || pauseRecognitionForAudio || isBrowserListening || serverChunkMode) {
            return;
          }
          startBrowserSpeech().catch((err) => {
            addMessage('system', 'System:', `Επανεκκίνηση STT απέτυχε: ${err.message || err}`);
          });
        }, Math.max(250, Math.round(delayMs || MIN_RESTART_DELAY_MS)));
      }

      function updateControls() {
        startMicBtn.disabled = callModeActive || isRecording || isBrowserListening;
        stopMicBtn.disabled = !(callModeActive || isRecording || isBrowserListening);
      }

      function normalizeTranscript(text) {
        return String(text || '').toLowerCase().replace(/\s+/g, ' ').trim();
      }

      function normalizeIntentText(text) {
        return normalizeTranscript(text)
          .normalize('NFD')
          .replace(/[\u0300-\u036f]/g, '');
      }

      function isExitIntent(text) {
        const norm = normalizeIntentText(text);
        if (!norm) return false;

        if (norm.includes('με λενε') && (norm.includes('γεια') || norm.includes('καλημερα'))) {
          return false;
        }

        const explicitPhrases = [
          'δεν θελω αλλο',
          'δεν θελω να συνεχισ',
          'κλεισε την κληση',
          'τερματισ',
          'σταματα',
          'τελος κλησης',
        ];
        if (explicitPhrases.some((phrase) => norm.includes(phrase))) {
          return true;
        }

        const goodbyeTokens = ['αντιο', 'bye', 'goodbye', 'τα λεμε'];
        const tokenCount = norm.split(/\s+/).filter(Boolean).length;
        if (goodbyeTokens.some((token) => norm.includes(token)) && tokenCount <= 6) {
          return true;
        }

        if (norm === 'γεια' || norm === 'οχι γεια' || norm === 'αντιο σας') {
          return true;
        }
        return false;
      }

      function tokenizeTranscript(text) {
        return normalizeTranscript(text)
          .replace(/[^\p{L}\p{N}\s]/gu, ' ')
          .split(/\s+/)
          .map((token) => token.trim())
          .filter((token) => token.length > 1);
      }

      function calculateTokenOverlap(a, b) {
        const aTokens = tokenizeTranscript(a);
        const bTokens = tokenizeTranscript(b);
        if (!aTokens.length || !bTokens.length) return 0;

        const aSet = new Set(aTokens);
        let shared = 0;
        for (const token of bTokens) {
          if (aSet.has(token)) {
            shared += 1;
          }
        }
        return shared / Math.max(1, Math.min(aSet.size, bTokens.length));
      }

      function rememberAssistantUtterance(text) {
        lastAssistantNorm = normalizeTranscript(text);
        lastAssistantTs = Date.now();
      }

      function isLikelyAssistantEcho(normText) {
        if (!normText || !lastAssistantNorm) return false;
        const ageMs = Date.now() - lastAssistantTs;
        if (ageMs > 8000) return false;

        if (lastAssistantNorm.includes(normText) || normText.includes(lastAssistantNorm)) {
          return true;
        }

        const overlap = calculateTokenOverlap(lastAssistantNorm, normText);
        return overlap >= 0.72;
      }

      function shouldDropTranscript(text) {
        const norm = normalizeTranscript(text);
        if (!norm) return { drop: true, reason: 'empty' };

        if (isLikelyAssistantEcho(norm)) {
          return { drop: true, reason: 'echo' };
        }

        const now = Date.now();
        if (norm === lastTranscriptNorm && now - lastTranscriptTs < 4500) {
          return { drop: true, reason: 'duplicate' };
        }
        lastTranscriptNorm = norm;
        lastTranscriptTs = now;
        return { drop: false, reason: '' };
      }

      async function postJson(path, payload) {

        const response = await fetch(path, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const details = await response.text();
          throw new Error(`HTTP ${response.status}: ${details}`);
        }
        return await response.json();
      }

      async function ensureSession() {
        if (sessionId) return sessionId;

        const body = {
          user_id: 'mac-voice-user',
          channel: 'webrtc',
          locale: 'el-GR',
        };

        const response = await postJson('/v1/sessions/start', body);
        sessionId = response.session_id;
        setMeta(`Κατάσταση: έτοιμο | session=${sessionId}`);
        addMessage('system', 'System:', 'Νέα συνεδρία ξεκίνησε.');
        return sessionId;
      }

      function toAudioUrl(audioChunkRef) {
        if (!audioChunkRef || typeof audioChunkRef !== 'string') return null;
        if (!audioChunkRef.startsWith('file://')) return null;

        const filename = audioChunkRef.split('/').pop();
        if (!filename) return null;
        return `/v1/audio/${encodeURIComponent(filename)}`;
      }

      function browserSpeechSupported() {
        return typeof window.SpeechRecognition !== 'undefined' || typeof window.webkitSpeechRecognition !== 'undefined';
      }

      async function speakWithBrowserTTS(text) {
        const phrase = String(text || '').trim();
        if (!phrase) return false;
        if (!window.speechSynthesis || typeof window.SpeechSynthesisUtterance === 'undefined') {
          return false;
        }

        return await new Promise((resolve) => {
          try {
            const utterance = new SpeechSynthesisUtterance(phrase);
            utterance.lang = 'el-GR';
            utterance.rate = 0.95;
            utterance.pitch = 1.0;
            const voices = window.speechSynthesis.getVoices() || [];
            const greekVoice = voices.find((voice) => String(voice.lang || '').toLowerCase().startsWith('el'));
            if (greekVoice) {
              utterance.voice = greekVoice;
            }
            utterance.onend = () => resolve(true);
            utterance.onerror = () => resolve(false);
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
          } catch (_) {
            resolve(false);
          }
        });
      }

      async function playAudioUrl(audioUrl) {
        if (!audioUrl) return false;
        try {
          if (currentAudio) {
            try {
              currentAudio.pause();
            } catch (_) {
              // no-op
            }
            currentAudio = null;
          }

          const audio = new Audio(audioUrl);
          audio.preload = 'auto';
          audio.volume = 1.0;
          currentAudio = audio;

          const ok = await new Promise((resolve) => {
            let settled = false;
            const finish = (value) => {
              if (settled) return;
              settled = true;
              resolve(value);
            };

            audio.addEventListener('ended', () => finish(true), { once: true });
            audio.addEventListener('error', () => finish(false), { once: true });

            const playPromise = audio.play();
            if (playPromise && typeof playPromise.catch === 'function') {
              playPromise.catch(() => finish(false));
            }
          });

          currentAudio = null;
          return Boolean(ok);
        } catch (_) {
          currentAudio = null;
          return false;
        }
      }

      async function playOpeningGreeting() {
        addMessage('bot', 'Thalpo:', CALL_OPENING_GREETING);
        rememberAssistantUtterance(CALL_OPENING_GREETING);
        pauseRecognitionForAudio = true;
        addStage('Αναπαραγωγή αρχικού χαιρετισμού...');
        let played = false;
        try {
          const response = await postJson('/v1/mac/opening-greeting', {
            session_id: sessionId,
            text: CALL_OPENING_GREETING,
          });
          const audioUrl = toAudioUrl(response.audio_chunk_ref || '');
          if (audioUrl) {
            played = await playAudioUrl(audioUrl);
          }
        } catch (_) {
          played = false;
        }

        if (!played) {
          addStage('Fallback σε browser TTS για αρχικό χαιρετισμό...');
          played = await speakWithBrowserTTS(CALL_OPENING_GREETING);
        }

        if (played) {
          addStage('Ο αρχικός χαιρετισμός ολοκληρώθηκε.');
        } else {
          addMessage('system', 'Audio:', 'Δεν μπόρεσα να παίξω τον αρχικό χαιρετισμό.');
        }
        pauseRecognitionForAudio = false;
      }

      async function sendTurn(text) {
        const trimmed = (text || '').trim();
        if (!trimmed) return;

        await ensureSession();
        addMessage('user', 'Εσύ:', trimmed);

        if (callModeActive && isExitIntent(trimmed)) {
          const closingText = 'Βεβαίως, κλείνω την κλήση τώρα. Να είστε καλά και τα λέμε σύντομα.';
          addStage('Εντοπίστηκε πρόθεση τερματισμού από τον χρήστη.');
          addMessage('bot', 'Thalpo:', closingText);
          rememberAssistantUtterance(closingText);

          pauseRecognitionForAudio = true;
          if (recognition && isBrowserListening) {
            try {
              recognition.stop();
            } catch (_) {
              // no-op
            }
          }

          const spoken = await speakWithBrowserTTS(closingText);
          if (spoken) {
            addStage('Ο αποχαιρετισμός ολοκληρώθηκε.');
          } else {
            addMessage('system', 'Audio:', 'Δεν ήταν δυνατή η αναπαραγωγή αποχαιρετισμού.');
          }
          await stopCallMode();
          return;
        }

        addStage('Στέλνω turn στο Orchestrator...');

        const payload = {
          session_id: sessionId,
          user_id: 'mac-voice-user',
          raw_text: trimmed,
        };

        const response = await postJson('/v1/turns/process', payload);
        const assistantText = (response.assistant_text || '').trim() || '(χωρίς απάντηση)';
        addMessage('bot', 'Thalpo:', assistantText);
        rememberAssistantUtterance(assistantText);

        const ms = response.latency_ms && response.latency_ms.total;
        if (typeof ms === 'number') {
          setMeta(`Κατάσταση: έτοιμο | latency ${ms}ms | session=${sessionId}`);
        }
        if (response && response.latency_ms) {
          const latency = response.latency_ms;
          addStage(
            `Latency turn: VAD ${latency.vad ?? '-'}ms | STT ${latency.stt ?? '-'}ms | LLM ${latency.llm ?? '-'}ms | TTS ${latency.tts ?? '-'}ms | TOTAL ${latency.total ?? '-'}ms`
          );
        }

        const audioUrl = toAudioUrl(response.audio_chunk_ref || '');
        let played = false;

        if (callModeActive) {
          clearRestartTimer();
          noTranscriptCycles = 0;
          pauseRecognitionForAudio = true;
          if (recognition && isBrowserListening) {
            try {
              recognition.stop();
            } catch (_) {
              // no-op
            }
          }
        }

        if (audioUrl) {
          try {
            played = await playAudioUrl(audioUrl);
            if (!played) {
              addMessage('system', 'Audio:', 'Η αναπαραγωγή MP3 απέτυχε. Θα χρησιμοποιήσω browser φωνή.');
            }
          } catch (_) {
            played = false;
          }
        }

        if (!played) {
          addStage('Fallback σε browser TTS...');
          const browserSpoken = await speakWithBrowserTTS(assistantText);
          if (!browserSpoken) {
            addMessage('system', 'Audio:', 'Δεν ήταν δυνατή η αναπαραγωγή φωνής.');
          } else {
            addStage('Browser TTS ολοκληρώθηκε.');
          }
        } else {
          addStage('Αναπαραγωγή MP3 ολοκληρώθηκε.');
        }

        if (callModeActive && browserSpeechSupported() && !serverChunkMode) {
          pauseRecognitionForAudio = false;
          addStage('Επιστροφή σε ακρόαση (STT)...');
          scheduleBrowserRestart(350);
          armSilenceHintTimer();
        }
      }

      async function transcribeAudioBlob(blob) {
        const ext = blob.type.includes('mp4') ? 'm4a' : (blob.type.includes('ogg') ? 'ogg' : 'webm');
        const file = new File([blob], `voice.${ext}`, { type: blob.type || 'audio/webm' });

        const form = new FormData();
        form.append('file', file);
        form.append('language', 'el');

        const response = await fetch('/v1/mac/transcribe', {
          method: 'POST',
          body: form,
        });

        if (!response.ok) {
          const details = await response.text();
          throw new Error(`STT failed (${response.status}): ${details}`);
        }

        return await response.json();
      }

      async function recordOneServerChunk(durationMs = 4200) {
        await ensureSession();

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          throw new Error('Ο browser δεν υποστηρίζει getUserMedia.');
        }
        if (typeof MediaRecorder === 'undefined') {
          throw new Error('Ο browser δεν υποστηρίζει MediaRecorder.');
        }

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        const chunks = [];

        recorder.ondataavailable = (event) => {
          if (event.data && event.data.size > 0) {
            chunks.push(event.data);
          }
        };

        recorder.start();
        addStage('Server STT chunk recording...');
        await sleepMs(durationMs);
        await new Promise((resolve) => {
          recorder.onstop = resolve;
          recorder.stop();
        });

        for (const track of stream.getTracks()) {
          track.stop();
        }

        const blob = new Blob(chunks, { type: chunks[0]?.type || 'audio/webm' });
        const sttStarted = performance.now();
        const stt = await transcribeAudioBlob(blob);
        const transcript = (stt.transcript || '').trim();
        const sttElapsed = Math.round(performance.now() - sttStarted);
        addStage(`Server STT: provider=${stt.provider || 'unknown'} | latency=${stt.latency_ms ?? sttElapsed}ms`);

        if (transcript) {
          silenceHints = 0;
          queueTranscript(transcript);
        } else {
          addStage('Server STT: χωρίς transcript σε αυτό το chunk.');
        }
      }

      async function startServerChunkMode() {
        if (serverChunkMode) {
          return;
        }
        if (!serverSttUsable()) {
          addStage('Server STT είναι προσωρινά ανενεργό. Συνεχίζω με browser STT.');
          return;
        }
        serverChunkMode = true;
        serverChunkAbort = false;
        silenceHints = 0;
        clearSilenceHintTimer();
        addStage('Server STT mode ενεργό (auto chunks).');

        while (callModeActive && !serverChunkAbort) {
          try {
            await recordOneServerChunk();
          } catch (err) {
            const errText = String(err && err.message ? err.message : err);
            addMessage('system', 'System:', `Σφάλμα server STT mode: ${errText}`);
            if (
              errText.includes('(401)') ||
              errText.toLowerCase().includes('auth failed')
            ) {
              serverSttDisabled = true;
              serverChunkAbort = true;
              addStage('Απενεργοποιώ server STT (auth error). Συνεχίζω με browser STT μόνο.');
            }
            await sleepMs(600);
          }

          if (!callModeActive || serverChunkAbort) {
            break;
          }

          let waits = 0;
          while ((processingTurns || pauseRecognitionForAudio) && callModeActive && !serverChunkAbort && waits < 80) {
            await sleepMs(200);
            waits += 1;
          }
          await sleepMs(200);
        }

        serverChunkMode = false;
        if (callModeActive && browserSpeechSupported()) {
          armSilenceHintTimer();
          addStage('Επιστροφή σε browser STT mode.');
          await startBrowserSpeech();
        } else if (callModeActive && !browserSpeechSupported() && serverSttDisabled) {
          callModeActive = false;
          addMessage('system', 'System:', 'Δεν υπάρχει διαθέσιμο STT (server auth failed + browser unsupported).');
          updateControls();
        }
      }

      async function processTurnQueue() {
        if (processingTurns) return;
        processingTurns = true;

        try {
          while (pendingTurns.length > 0) {
            const transcript = pendingTurns.shift();
            if (!transcript) continue;
            try {
              await sendTurn(transcript);
            } catch (err) {
              addMessage('system', 'System:', `Σφάλμα turn: ${err.message || err}`);
            }
          }
        } finally {
          processingTurns = false;
        }
      }

      function queueTranscript(text) {
        const transcript = String(text || '').trim();
        if (!transcript) return;

        const dropDecision = shouldDropTranscript(transcript);
        if (dropDecision.drop) {
          if (dropDecision.reason === 'echo') {
            addStage('Αγνόηση transcript (πιθανό echo από τη φωνή της Thalpo).');
          } else if (dropDecision.reason === 'duplicate') {
            addStage('Αγνόηση διπλού transcript (dedupe).');
          }
          return;
        }

        noTranscriptCycles = 0;
        clearRestartTimer();
        clearSilenceHintTimer();
        addMessage('system', 'STT:', transcript);
        pendingTurns.push(transcript);
        addStage(`Queue turn (${pendingTurns.length} pending).`);
        processTurnQueue();
      }

      function stopAndReleaseStream() {
        if (mediaStream) {
          for (const track of mediaStream.getTracks()) {
            track.stop();
          }
          mediaStream = null;
        }
        mediaRecorder = null;
        isRecording = false;
      }

      async function startRecording() {
        await ensureSession();

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
          throw new Error('Ο browser δεν υποστηρίζει getUserMedia.');
        }
        if (typeof MediaRecorder === 'undefined') {
          throw new Error('Ο browser δεν υποστηρίζει MediaRecorder.');
        }

        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(mediaStream);
        recordedChunks = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data && event.data.size > 0) recordedChunks.push(event.data);
        };

        mediaRecorder.start();
        isRecording = true;
        setMeta(`Κατάσταση: γράφω... | session=${sessionId}`);
        addMessage('system', 'Mic:', 'Ξεκίνησε η εγγραφή. Μιλήστε τώρα.');
      }

      async function startBrowserSpeech() {
        if (serverChunkMode) {
          return;
        }
        await ensureSession();

        if (!browserSpeechSupported()) {
          throw new Error('Ο browser δεν υποστηρίζει SpeechRecognition.');
        }

        if (!recognition) {
          const SpeechRecognitionCtor = window.SpeechRecognition || window.webkitSpeechRecognition;
          recognition = new SpeechRecognitionCtor();
          recognition.lang = 'el-GR';
          recognition.interimResults = true;
          recognition.continuous = false;

          recognition.onstart = () => {
            isBrowserListening = true;
            setMeta(`Κατάσταση: ακούω... | session=${sessionId}`);
            addStage('Browser STT ξεκίνησε.');
            updateControls();
          };

          recognition.onresult = (event) => {
            if (pauseRecognitionForAudio) {
              return;
            }
            let interimText = '';
            for (let i = event.resultIndex; i < event.results.length; i += 1) {
              const result = event.results[i];
              const chunk = (result[0]?.transcript || '').trim();
              if (!chunk) continue;
              if (result.isFinal) {
                cycleFinalTranscript += `${chunk} `;
              } else {
                interimText += `${chunk} `;
              }
            }
            if (interimText.trim()) {
              cycleInterimTranscript = interimText.trim();
              setMeta(`Κατάσταση: ακούω \"${interimText.trim()}\" | session=${sessionId}`);
            }
          };

          recognition.onerror = (event) => {
            if (event.error === 'aborted' || event.error === 'no-speech') {
              return;
            }
            addMessage('system', 'STT:', `Browser STT σφάλμα: ${event.error || 'unknown'}`);
            if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
              if (serverSttUsable() && !serverChunkMode) {
                addStage('Browser STT blocked. Switch σε server STT mode.');
                startServerChunkMode().catch((err) => {
                  addMessage('system', 'System:', `Σφάλμα server STT mode: ${err.message || err}`);
                });
                return;
              }
              callModeActive = false;
              updateControls();
            }
          };

          recognition.onend = () => {
            isBrowserListening = false;
            if (!callModeActive) {
              setMeta(`Κατάσταση: έτοιμο | session=${sessionId}`);
              updateControls();
              return;
            }

            const transcript = cycleFinalTranscript.trim() || cycleInterimTranscript.trim();
            cycleFinalTranscript = '';
            cycleInterimTranscript = '';

            if (transcript) {
              addStage('Browser STT cycle ολοκληρώθηκε, βρέθηκε transcript.');
              noTranscriptCycles = 0;
              clearRestartTimer();
              queueTranscript(transcript);
              return;
            }

            if (!pauseRecognitionForAudio) {
              noTranscriptCycles += 1;
              const restartDelay = Math.min(
                MIN_RESTART_DELAY_MS + (noTranscriptCycles - 1) * 250,
                MAX_RESTART_DELAY_MS
              );
              if (noTranscriptCycles === 1 || noTranscriptCycles % 3 === 0) {
                addStage(`Δεν βρέθηκε transcript, επανεκκίνηση STT (${restartDelay}ms).`);
              }
              scheduleBrowserRestart(restartDelay);
            }
          };
        }

        if (isBrowserListening || pauseRecognitionForAudio) return;
        cycleFinalTranscript = '';
        cycleInterimTranscript = '';
        recognition.start();
      }

      async function stopRecordingAndSend() {
        if (!mediaRecorder || !isRecording) return;

        setMeta(`Κατάσταση: επεξεργασία STT... | session=${sessionId}`);

        await new Promise((resolve) => {
          mediaRecorder.onstop = resolve;
          mediaRecorder.stop();
        });

        const blob = new Blob(recordedChunks, { type: recordedChunks[0]?.type || 'audio/webm' });
        stopAndReleaseStream();

        try {
          const sttStarted = performance.now();
          const stt = await transcribeAudioBlob(blob);
          const transcript = (stt.transcript || '').trim();
          const sttElapsed = Math.round(performance.now() - sttStarted);
          addStage(
            `Server STT: provider=${stt.provider || 'unknown'} | latency=${stt.latency_ms ?? sttElapsed}ms`
          );

          if (!transcript) {
            addMessage('system', 'STT:', 'Δεν αναγνωρίστηκε κείμενο από την εγγραφή.');
            setMeta(`Κατάσταση: έτοιμο | session=${sessionId}`);
            return;
          }

          addMessage('system', 'STT:', transcript);
          await sendTurn(transcript);
        } catch (err) {
          const errorText = String(err && err.message ? err.message : err);
          addMessage('system', 'System:', `Σφάλμα STT: ${errorText}`);

          if (errorText.includes('STT failed (429)')) {
            addMessage(
              'system',
              'System:',
              'Το OpenAI STT είναι σε quota/rate limit. Περνάω σε browser STT.'
            );
            setMeta(`Κατάσταση: browser STT fallback | session=${sessionId}`);
            if (browserSpeechSupported()) {
              try {
                await startBrowserSpeech();
                return;
              } catch (fallbackErr) {
                addMessage('system', 'System:', `Fallback STT σφάλμα: ${fallbackErr.message || fallbackErr}`);
              }
            }
          }

          setMeta(`Κατάσταση: σφάλμα STT | session=${sessionId}`);
        }
      }

      async function startCallMode() {
        await ensureSession();
        callModeActive = true;
        callStartedAt = Date.now();
        silenceHints = 0;
        silenceHintLogTs = 0;
        noTranscriptCycles = 0;
        clearRestartTimer();
        lastAssistantNorm = '';
        lastAssistantTs = 0;
        serverSttDisabled = false;
        noServerSttNoticeShown = false;
        serverChunkAbort = false;
        pendingTurns = [];
        addMessage('system', 'System:', 'Η κλήση άνοιξε. Μιλήστε ελεύθερα. Πατήστε Τερματισμός κλήσης για να κλείσει.');
        addStage(`Call mode ενεργό | STT=${browserSpeechSupported() ? 'browser' : (serverSttUsable() ? 'server' : 'none')} | TTS=${SERVER_STT_ENABLED ? 'google/cartesia/browser-fallback' : 'browser'}`);
        setMeta(`Κατάσταση: έναρξη κλήσης... | session=${sessionId}`);
        updateControls();

        await playOpeningGreeting();

        if (browserSpeechSupported()) {
          await startBrowserSpeech();
          armSilenceHintTimer();
          return;
        }

        if (serverSttUsable()) {
          addStage('Browser STT unavailable. Switch σε server STT mode.');
          await startServerChunkMode();
          return;
        }

        throw new Error('Δεν υπάρχει διαθέσιμο STT.');
      }

      async function stopCallMode() {
        callModeActive = false;
        callStartedAt = 0;
        serverChunkAbort = true;
        pendingTurns = [];
        noTranscriptCycles = 0;
        clearRestartTimer();
        clearSilenceHintTimer();

        if (isRecording) {
          await stopRecordingAndSend();
        }

        if (currentAudio) {
          try {
            currentAudio.pause();
          } catch (_) {
            // no-op
          }
          currentAudio = null;
        }

        if (recognition && isBrowserListening) {
          try {
            recognition.stop();
          } catch (_) {
            // no-op
          }
        }

        setMeta(`Κατάσταση: κλήση τερματίστηκε | session=${sessionId || '-'}`);
        addMessage('system', 'System:', 'Η κλήση τερματίστηκε.');
        updateControls();
      }

      startMicBtn.addEventListener('click', async () => {
        if (callModeActive || isRecording || isBrowserListening) return;
        try {
          await startCallMode();
        } catch (err) {
          addMessage('system', 'System:', `Σφάλμα μικροφώνου: ${err.message || err}`);
          setMeta(`Κατάσταση: σφάλμα μικροφώνου (${err.message || err})`);
          stopAndReleaseStream();
          callModeActive = false;
          updateControls();
        }
      });

      stopMicBtn.addEventListener('click', async () => {
        if (callModeActive) {
          const ageMs = Date.now() - callStartedAt;
          if (ageMs < 2500) {
            addStage('Αγνοήθηκε click τερματισμού (πολύ νωρίς, πιθανό διπλό-click).');
            return;
          }
          const shouldStop = window.confirm('Να τερματιστεί η κλήση;');
          if (!shouldStop) {
            addStage('Ακύρωση τερματισμού κλήσης.');
            return;
          }
          await stopCallMode();
          return;
        }
        if (isRecording) {
          await stopRecordingAndSend();
          return;
        }
        setMeta(`Κατάσταση: έτοιμο | session=${sessionId || '-'}`);
        updateControls();
      });

      newSessionBtn.addEventListener('click', async () => {
        if (callModeActive) {
          await stopCallMode();
        }
        sessionId = null;
        await ensureSession();
        updateControls();
      });

      sendTextBtn.addEventListener('click', async () => {
        const value = textInput.value;
        textInput.value = '';
        try {
          await sendTurn(value);
        } catch (err) {
          addMessage('system', 'System:', `Σφάλμα: ${err.message || err}`);
        }
      });

      textInput.addEventListener('keydown', async (event) => {
        if (event.key !== 'Enter') return;
        event.preventDefault();
        sendTextBtn.click();
      });

      (async () => {
        try {
          updateControls();
          await ensureSession();
          if (!SERVER_STT_ENABLED && !browserSpeechSupported()) {
            addMessage(
              'system',
              'System:',
              'Ο browser δεν υποστηρίζει SpeechRecognition και δεν έχει οριστεί OPENAI_API_KEY.'
            );
          }
        } catch (err) {
          setMeta(`Κατάσταση: σφάλμα (${err.message || err})`);
          addMessage('system', 'System:', `Σφάλμα αρχικοποίησης: ${err.message || err}`);
        }
      })();
    </script>
  </body>
</html>
""".replace("__SERVER_STT_ENABLED__", "true" if server_stt_enabled else "false")
