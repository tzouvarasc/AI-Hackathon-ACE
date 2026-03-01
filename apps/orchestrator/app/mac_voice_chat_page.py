from __future__ import annotations


def build_mac_voice_chat_html(*, server_stt_enabled: bool) -> str:
    return """<!doctype html>
<html lang=\"el\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Thalpo Voice Chat (Greek)</title>
    <style>
      :root {
        --bg: #f4f6fb;
        --card: #ffffff;
        --ink: #1c2433;
        --muted: #5a6474;
        --line: #d9dfeb;
        --primary: #0d5bd6;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        background: radial-gradient(circle at 15% 10%, #dce8ff 0%, var(--bg) 35%, #eef2fb 100%);
        color: var(--ink);
        font: 16px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      .wrap {
        max-width: 920px;
        margin: 28px auto;
        padding: 0 16px;
      }
      .card {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 14px;
        box-shadow: 0 10px 28px rgba(23, 37, 74, 0.08);
        padding: 16px;
      }
      h1 { margin: 0 0 10px; font-size: 24px; }
      p { margin: 0 0 12px; color: var(--muted); }
      .row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 12px;
      }
      button {
        border: 1px solid var(--line);
        border-radius: 10px;
        background: #fff;
        color: var(--ink);
        padding: 9px 14px;
        font-weight: 600;
        cursor: pointer;
      }
      button.primary {
        background: var(--primary);
        border-color: var(--primary);
        color: #fff;
      }
      button:disabled { opacity: 0.55; cursor: not-allowed; }
      input[type=\"text\"] {
        flex: 1;
        min-width: 220px;
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 10px 12px;
        font-size: 16px;
      }
      .meta {
        font-size: 13px;
        color: var(--muted);
        margin: 0 0 10px;
      }
      .log {
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 10px;
        min-height: 340px;
        max-height: 52vh;
        overflow: auto;
        background: #fbfcff;
      }
      .msg { margin: 0 0 10px; padding: 8px 10px; border-radius: 10px; }
      .msg.user { background: #edf4ff; }
      .msg.bot { background: #f7f2ff; }
      .msg.system { background: #eef7f2; color: #2f5f46; }
      .label { font-weight: 700; margin-right: 6px; }
      .warn {
        margin-top: 10px;
        color: #8b3a00;
        background: #fff6ef;
        border: 1px solid #ffd9bf;
        border-radius: 10px;
        padding: 8px 10px;
        font-size: 13px;
      }
    </style>
  </head>
  <body>
    <div class=\"wrap\">
      <div class=\"card\">
        <h1>Thalpo Greek Voice Chat</h1>
        <p>Μιλήστε στα Ελληνικά. Πατήστε <strong>Έναρξη κλήσης</strong> μία φορά για συνεχή συνομιλία και <strong>Τερματισμός κλήσης</strong> όταν θέλετε να κλείσετε.</p>

        <div class=\"meta\" id=\"meta\">Κατάσταση: αρχικοποίηση...</div>

        <div class=\"row\">
          <button id=\"startMic\" class=\"primary\">Έναρξη κλήσης</button>
          <button id=\"stopMic\">Τερματισμός κλήσης</button>
          <button id=\"newSession\">Νέα συνεδρία</button>
        </div>

        <div class=\"row\">
          <input id=\"textInput\" type=\"text\" placeholder=\"Ή γράψτε εδώ και πατήστε Enter\" />
          <button id=\"sendText\">Αποστολή</button>
        </div>

        <div id=\"log\" class=\"log\"></div>

        <div class=\"warn\">
          Λειτουργία κλήσης: Browser STT (Safari/Chrome). Server STT ενεργοποιείται μόνο αν είναι πλήρως ρυθμισμένο.
        </div>
      </div>
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
