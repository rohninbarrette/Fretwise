# Fretwise

A guitar app that runs in the browser and can be installed on an iPhone home screen.

- **Finder**: tap notes on a vertical fretboard and it names the chord, with inversion, keys and missing notes.
- **Chords**: 64 chord types in every key, from triads to altered dominants and named chords (So What, Petrushka, Bond), with search, slash chords and favourites.
- **Scales**: 29 scales in every key, on a full horizontal fretboard or one position at a time.
- **Keys**: circle of fifths with every chord in the selected key and common progressions.
- **Song**: build a chord chart, transpose it, play it back with strum patterns, save it, copy it, and see which scales to solo with.
- **Practice**: metronome with tap tempo, strumming patterns and ear training.
- **Tuner**: a full-screen microphone tuner with an LED arc display, in the style of a stompbox pedal tuner.
- **Settings**: 17 tunings plus custom, capo, and left-handed mode.

## Files

- `fretwise.html` is the only source file. Edit this one.
- `build.py` wraps it into `docs/index.html` and writes the manifest, offline service worker and icons. Run `python3 build.py` after every change.
- `docs/` is what gets hosted (GitHub Pages serves this folder).

## Try it locally

```bash
python3 build.py && python3 -m http.server 8765 --directory docs
```

Then open http://localhost:8765.

## Put it on an iPhone

1. Host `docs/` on GitHub Pages (Settings → Pages → Deploy from a branch → `main`, folder `/docs`). It is live at https://rohninbarrette.github.io/Fretwise/.
2. Open the Pages address in Safari on the iPhone.
3. Tap Share → Add to Home Screen.

It then opens full screen like a normal app and works offline after the first visit. New versions show up the next time it is opened with an internet connection.
