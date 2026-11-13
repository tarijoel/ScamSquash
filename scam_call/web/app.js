const get = (id) => document.getElementById(id);
const start = get("start");
const end = get("end");
const speaker = get("speaker");
const download = get("download");
const labels = {caller: "Caller", receiver: "Receiver", assistant: "Assistant"};
let completed;
const status = get("status");
const voice = get("voice");
let active;

function append(call, speaker, text) {
  call.turns.push({speaker, text});
  const line = document.createElement("li");
  line.textContent = labels[speaker] + ": " + text;
  get("transcript").append(line);
}

async function post(path, body, type) {
  const response = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": type},
    body,
  });
  if (!response.ok) {
    throw new Error(type === "application/sdp" ? await response.text() : "Could not review the transcript.");
  }
  return response;
}

async function review(call) {
  const result = await post("/review", JSON.stringify(call.turns), "application/json");
  return result.json();
}

async function finish(call, message = "Call ended") {
  if (active !== call || call.ended) return;
  call.ended = true;
  clearTimeout(call.timer);
  call.mic?.getTracks().forEach((track) => track.stop());
  call.peer.close();
  voice.srcObject = null;
  get("handoff").hidden = true;
  end.disabled = true;
  status.textContent = message;
  try {
    if (call.turns.length) get("report").textContent = (await review(call)).report;
  } catch {
    get("report").textContent = "Could not generate the draft. The transcript is still visible.";
  } finally {
    completed = call.turns;
    download.disabled = !completed.length;
    speaker.disabled = false;
    active = null;
    start.disabled = false;
  }
}

function listen(call) {
  clearTimeout(call.timer);
  call.phase = "listening";
  call.track.enabled = true;
  speaker.disabled = call.takenOver;
  status.textContent = call.takenOver ? "Listening to the caller." : "Listening to both people. Select the speaker before each turn.";
}

function reply(call, goal) {
  if (!call.takenOver) return;
  call.phase = "replying";
  call.track.enabled = false;
  speaker.disabled = true;
  status.textContent = "Assistant replying…";
  call.channel.send(JSON.stringify({
    type: "response.create",
    response: {
      output_modalities: ["audio"],
      instructions: goal + " Keep the reply brief. Never provide personal information, credentials, codes, or payment.",
    },
  }));
  clearTimeout(call.timer);
  call.timer = setTimeout(() => finish(call, "The voice response timed out."), 30000);
}

function followUp(call) {
  if (call.followUps >= 3) {
    finish(call);
    return;
  }
  call.followUps += 1;
  reply(call, "As the fictional recipient, acknowledge what the caller just said and ask one natural question about a missing detail: claimed organization, callback number, requested amount, or payment method. Avoid repeating questions.");
}

async function handleEvent(call, event) {
  if (active !== call || call.ended) return;
  switch (event.type) {
    case "input_audio_buffer.speech_started":
      if (call.phase === "listening") {
        call.turnSpeaker = call.takenOver ? "caller" : speaker.value;
        speaker.disabled = true;
      }
      break;
    case "input_audio_buffer.speech_stopped":
      if (call.phase === "listening") {
        call.phase = "transcribing";
        call.track.enabled = false;
        status.textContent = "Checking what the caller said…";
        call.timer = setTimeout(() => finish(call, "Transcription timed out."), 20000);
      }
      break;
    case "conversation.item.input_audio_transcription.completed": {
      if (!["listening", "transcribing"].includes(call.phase)) return;
      clearTimeout(call.timer);
      if (!event.transcript?.trim()) {
        listen(call);
        return;
      }
      call.phase = "checking";
      call.track.enabled = false;
      append(call, call.takenOver ? "caller" : (call.turnSpeaker ?? speaker.value), event.transcript.trim());
      call.turnSpeaker = null;
      const {evidence} = await review(call);
      if (call.ended) return;
      if (evidence.length && !call.takenOver) {
        call.takenOver = true;
        speaker.value = "caller";
        get("evidence").replaceChildren(...evidence.map((item) => {
          const line = document.createElement("li");
          line.textContent = `Turn ${item.turn} · ${item.reason} · “${item.quote}”`;
          return line;
        }));
        get("handoff").hidden = false;
      }
      if (call.takenOver) {
        followUp(call);
      } else if (call.turns.length >= 70) {
        finish(call, "Demo turn limit reached.");
      } else {
        listen(call);
      }
      break;
    }
    case "response.output_audio_transcript.done":
      if (call.phase === "replying" && event.transcript?.trim()) {
        append(call, "assistant", event.transcript.trim());
      }
      break;
    case "output_audio_buffer.stopped":
      if (call.phase === "replying") listen(call);
      break;
    case "response.done":
      if (event.response?.status !== "completed") {
        await finish(call, "The assistant could not complete its reply.");
      }
      break;
    case "conversation.item.input_audio_transcription.failed":
      await finish(call, "The voice service could not transcribe the caller.");
      break;
    case "error":
      await finish(call, event.error?.message || "The voice service returned an error.");
      break;
  }
}

start.onclick = async () => {
  if (!window.RTCPeerConnection || !navigator.mediaDevices?.getUserMedia) {
    status.textContent = "This browser cannot access a microphone here. Open the localhost URL in Chrome or Safari.";
    return;
  }
  start.disabled = true;
  download.disabled = true;
  speaker.value = "receiver";
  get("transcript").replaceChildren();
  get("report").textContent = "The draft will appear when a flagged call ends.";
  status.textContent = "Connecting microphone…";
  const call = {
    turns: [], takenOver: false, followUps: 0, ended: false,
    phase: "connecting", peer: new RTCPeerConnection(),
  };
  active = call;
  end.disabled = false;
  try {
    call.mic = await navigator.mediaDevices.getUserMedia({audio: {echoCancellation: true}});
    if (call.ended) {
      call.mic.getTracks().forEach((track) => track.stop());
      return;
    }
    [call.track] = call.mic.getAudioTracks();
    call.track.enabled = false;
    call.peer.addTrack(call.track, call.mic);
    call.peer.ontrack = (event) => { voice.srcObject = event.streams[0]; };
    call.peer.onconnectionstatechange = () => {
      if (call.peer.connectionState === "failed") finish(call, "The voice connection failed.");
    };
    call.channel = call.peer.createDataChannel("oai-events");
    call.channel.onopen = () => {
      if (!call.ended) listen(call);
    };
    call.channel.onclose = () => finish(call, "Voice connection closed.");
    call.channel.onmessage = (message) => {
      handleEvent(call, JSON.parse(message.data)).catch((error) => finish(call, error.message));
    };
    const offer = await call.peer.createOffer();
    await call.peer.setLocalDescription(offer);
    const response = await post("/session", offer.sdp, "application/sdp");
    if (call.ended) return;
    await call.peer.setRemoteDescription({type: "answer", sdp: await response.text()});
    if (call.phase === "connecting" && !call.ended) {
      call.timer = setTimeout(() => finish(call, "The voice connection timed out."), 20000);
    }
  } catch (error) {
    await finish(call, error.message || "Could not start the voice demo.");
  }
};

download.onclick = () => {
  if (!completed?.length) return;
  const transcript = completed.map((turn, i) => `${i + 1}. ${labels[turn.speaker]}: ${turn.text}`).join("\n");
  const file = new Blob([transcript], {type: "text/plain;charset=utf-8"});
  const url = URL.createObjectURL(file);
  const link = document.createElement("a");
  link.href = url;
  link.download = "scamsquash-transcript.txt";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};

end.onclick = () => {
  if (active) finish(active);
};
