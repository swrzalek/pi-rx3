# Controllers and pads

The bridge translates supported XML bindings into RX3 input events; it does not run Mixxx JavaScript. Restart RX3 after changing a profile or bridge code. MIDI mapping success does not certify physical controls, latency or audio routing.

## FLX6

The default configuration uses the pinned BiteDJ/Mixxx FLX6 XML downloaded by `./rx3 mapping`. To use an existing XML, set `[controller] mapping` and run `./rx3 mapping --offline`. Keep `[audio] card = DDJFLX6` and `[controller] midi_name = DDJ-FLX6` unless configuring another device.

Hot cues, default beat jumps and beat loops carry native bank intent; the adapter waits for a bank change before sending the pad press. Held presses remember their bank so a late release does not act on another bank. Rejected MIDI presses do not release an existing touchscreen hold. Same-bank overlapping touch/MIDI ownership remains unverified.

Native touch offers Hot Cue, Beat Loop, Slip Loop and Beat Jump. Tapping the active selector accesses its second bank; Slip Loop's second bank is Release FX. Highlighting follows native state and hides in Browse/mixer views. Touch-replay checks covered both decks, Slip Loop hold/release and Release FX activation/recovery; this does not establish physical feel, effect combinations or two-deck isolation.

## Experimental FLX4

In root `rx3.conf`:

```ini
[audio]
card = DDJFLX4
[controller]
midi_name = DDJ-FLX4
mapping = mappings/Pioneer-DDJ-FLX4.rx3.xml
```

The shipped [profile](../mappings/Pioneer-DDJ-FLX4.rx3.xml) uses 720 jog ticks/revolution. It covers both decks' load/play/cue, loops, sync/leader, quantize, tempo/range and jog; browsing/zoom; gain/EQ/filter/faders/crossfader/headphone controls; hot cues, beat loops and default beat-jump pads. Shift+jog keeps the bridge's grid-edit behavior. FLX6 resolution and behavior are unchanged.

Not covered: LED feedback, sampler, Pad FX/Beat FX, smart functions, memory-cue navigation, jog loop-end adjustment, hot-cue deletion, beat-jump size selection or exact rekordbox acceleration. Physical retesting is required, especially deck 2, master/headphone routing and touch alignment.

Reference MIDI addresses: [Mixxx FLX4 XML](https://github.com/mixxxdj/mixxx/blob/2.5/res/controllers/Pioneer-DDJ-FLX4.midi.xml); jog encoding: [Mixxx FLX4 script](https://github.com/mixxxdj/mixxx/blob/2.5/res/controllers/Pioneer-DDJ-FLX4-script.js). The profile is an RX3 input mapping, not a complete Mixxx preset.
