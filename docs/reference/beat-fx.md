# RX3 1.19 Beat FX adapter evidence

Verified against original rbp SHA-256
`60bcbd8876116bf09f0d8f747f95d7c7d3081ebd39d6fe14d56005a22f7f3b09`.
The recovered ELF retains symbols. No firmware or recovery key is committed.

- Physical panel dispatch at 0x3802a4/0x38030c sends BeatEffectSW (0x448b)
  and BfxChSW (0x448c) with operation 5, channel 0, selector in integer value.
- `MasterInnards::onEv_BeatEffectType` at 0x342ae0 translates selector indices
  0..13 into engine types `{6,5,13,7,14,1,4,9,10,2,3,12,8,11}`.
  Relative selection reads the native UI input index at MasterInnards +0x3c,
  reached through `*(0x026867c0)` -> +0x50 (Mixer) -> +0xa8 (MasterInnards).
  IUiObjManager::getMixer (0x31e054), Mixer::getMasterInnards (0x2cf890),
  and onEv_BeatEffectType stores (0x342b94/0x342c64) verify this chain.
  This preserves cycling while disabled: the engine type getter returns OFF
  then. Null/invalid UI state suppresses selection. After enqueueing, wait up
  to 100 ms for the native selected index to update before handling another
  command. Native audio processing continues independently.
- `MasterInnards::onEv_BeatEffectCh` at 0x343184 maps selector values to the
  same engine channel enum. `djengine::c_str(EnBeatEffectSelectChannel)` at
  0x50e54 identifies 0=PLAYER_0, 1=PLAYER_1, 5=MASTER.
- Physical panel dispatch at 0x38012c/0x38035c/0x3803b8 sends On/Off and Beat
  Prev/Next as ordinary operation 0/2 press/release pairs on channel 0.
- `DjEngineIF::isBeatEffectOn` at 0x4d1bc provides the native enabled state.
  The UI draw hook publishes this periodically; the MIDI worker rejects state
  older than two seconds and drives a fixed 2 Hz blink, independent of BPM.

FLX4 MIDI messages and 7-bit Level/Depth normalization follow Mixxx's 2.5
[Pioneer-DDJ-FLX4 XML](https://github.com/mixxxdj/mixxx/blob/2.5/res/controllers/Pioneer-DDJ-FLX4.midi.xml)
and [script](https://github.com/mixxxdj/mixxx/blob/2.5/res/controllers/Pioneer-DDJ-FLX4-script.js).
Its script identifies Beat FX LED output as `94 47 value`. Channel selector
messages independently enable channels 1 and 2; the adapter coalesces them
for 20 ms, mapping both enabled to master. Both disabled also selects master
rather than selecting an unrelated RX3 input. No effect enable change is
inferred from a routing transition.

These are static firmware and protocol checks, not evidence of audible
hardware behavior. Verify selection, timing, routing and LED behavior on a Pi.
