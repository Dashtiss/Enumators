# World's Most Basic CHIP-8 Emulator

A minimalistic (read: barely functional) CHIP-8 emulator written in Python using Pyglet. It's not fancy, but hey, it sort of works!

## Features (or lack thereof)
- Runs at a blazing 60Hz whether the ROM likes it or not
- Beautiful white rectangles on a black background (very avant-garde)
- Keyboard mapping that will make your fingers cry
- Zero sound implementation (it's a feature, not a bug - save your ears)
- Debugging messages that will flood your terminal like it's 1999

## Requirements
- Python 3.x (tested on whatever version I happened to have installed)
- Pyglet (for those sweet, sweet rectangles)
- A ROM file (good luck finding one)
- Low expectations

## How to Run
```bash
python main.py <path_to_rom>
```

## Keyboard Layout
```
Original CHIP-8    This Mess
1 2 3 C           1 2 3 4
4 5 6 D    ->     Q W E R
7 8 9 E           A S D F
A 0 B F           Z X C V
```

## Known Issues
- Everything might be upside down (or not, who knows?)
- The timing is probably wrong
- Some ROMs work, others don't (it's a surprise mechanic!)
- No sound, because silence is golden
- Probably not cycle-accurate (what even is a cycle?)

## Contributing
Please don't. But if you must:
1. Fork it
2. Fix it
3. Make it actually good
4. Wonder why you spent time on this

## License
MIT License (because I'm not responsible for any emotional damage caused by this code)

## Acknowledgments
- The CHIP-8 community (sorry about this)
- Pyglet (for making graphics slightly less painful)
- My keyboard (for enduring the abuse)
- The original CHIP-8 creators (please forgive me)
