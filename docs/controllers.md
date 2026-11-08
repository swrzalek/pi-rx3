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

The FLX4 bridge sends headphone CUE LED feedback for both channels from the native mixer input snapshot. Updates include touchscreen actions and are resent after MIDI output reconnection. Beat FX On/Off feedback is described below; other LEDs remain unsupported. MIDI output failures leave input handling active. The snapshot tracks dispatched actions rather than audio-engine acknowledgements.

Not covered: other LED feedback, sampler, Pad FX, smart functions, memory-cue navigation, jog loop-end adjustment, hot-cue deletion, beat-jump size selection or exact rekordbox acceleration. Physical retesting is required, especially deck 2, master/headphone routing and touch alignment.

Reference MIDI addresses: [Mixxx FLX4 XML](https://github.com/mixxxdj/mixxx/blob/2.5/res/controllers/Pioneer-DDJ-FLX4.midi.xml); jog encoding: [Mixxx FLX4 script](https://github.com/mixxxdj/mixxx/blob/2.5/res/controllers/Pioneer-DDJ-FLX4-script.js). The profile is an RX3 input mapping, not a complete Mixxx preset.

## FLX4 Beat FX

FX Select cycles through RX3's native effect list; Shift + Select goes backward.
Beat `<` / `>` changes the native beat setting. Level/Depth covers 0 to full
scale. The channel selector routes to deck 1, deck 2 or master (1+2).
On/Off toggles once per press and its LED blinks at 2 Hz while native FX is on.
Release FX and Shift + On/Off are not mapped. Existing settings remain until
controller messages arrive. Native verification details are in
[Beat FX adapter evidence](reference/beat-fx.md).

After updating, stop RX3, run `./rx3 build` and `./rx3 install`, then restart.
Test with distinguishable tracks on both decks: verify selection in both
directions, beat limits, depth endpoints, each routing position, and the LED
while enabled/disabled. Toggle FX on screen, restart the MIDI bridge, and
reconnect the controller to check feedback resynchronization. Physical testing
is still required before considering these controls validated.
