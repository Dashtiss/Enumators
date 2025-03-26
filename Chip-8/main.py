import sys
import pyglet
import random
import logging
from pyglet.graphics import Batch
from pyglet.shapes import Rectangle
from pyglet.window import key

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('CHIP-8')

class Chip8:
    def __init__(self):
        # Initialize Chip-8 components
        self.memory = [0] * 4096  # 4KB memory
        self.V = [0] * 16         # 16 registers
        self.I = 0                # Index register
        self.pc = 0x200           # Program counter starts at 0x200
        self.stack = []           # Stack for subroutine calls
        self.delay_timer = 0      # Delay timer
        self.sound_timer = 0      # Sound timer
        self.display = [0] * (64 * 32)  # 64x32 pixel display
        self.keys = [0] * 16      # Keypad state
        self.load_fontset()
        self.window = pyglet.window.Window(64 * 10, 32 * 10, "Chip-8 Emulator")
        self.window.push_handlers(self)
        self.pixel_size = 10  # Scale each pixel by 10x for better visibility
        self.keys_pressed = set()
        self.rectangles = []
        self.batch = Batch()
        # Initialize rectangles for each pixel
        for y in range(32):
            for x in range(64):
                rect = Rectangle(
                    x * self.pixel_size, (31 - y) * self.pixel_size,
                    self.pixel_size, self.pixel_size,
                    color=(255, 255, 255),
                    batch=self.batch
                )
                rect.visible = False
                self.rectangles.append(rect)
        self.test_display()  # Initialize display with test data for debugging
    def load_fontset(self):
        # Load the Chip-8 fontset into memory (0x000-0x1FF)
        fontset = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
        ]
        self.memory[:len(fontset)] = fontset

    def load_rom(self, rom_path):
        # Load ROM into memory starting at 0x200
        with open(rom_path, 'rb') as rom:
            rom_data = rom.read()
            self.memory[0x200:0x200 + len(rom_data)] = rom_data
            logger.info(f'Loaded ROM: {rom_path}, size: {len(rom_data)} bytes')

    def emulate_cycle(self):
        # Fetch opcode
        opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F
        nn = opcode & 0x00FF
        nnn = opcode & 0x0FFF

        logger.debug(f'Executing opcode: 0x{opcode:04X} at PC: 0x{self.pc:04X}')
        self.pc += 2
        # Decode and execute opcode (simplified example)
        if opcode == 0x00E0:  # Clear the display
            self.display = [0] * (64 * 32)
        elif opcode == 0x00EE:  # Return from subroutine
            self.pc = self.stack.pop()
        elif (opcode & 0xF000) == 0x1000:  # 1nnn: Jump to address
            self.pc = nnn
        elif (opcode & 0xF000) == 0x2000:  # 2nnn: Call subroutine
            self.stack.append(self.pc)
            self.pc = nnn
        elif (opcode & 0xF000) == 0x3000:  # 3xnn: Skip if Vx == nn
            if self.V[x] == nn:
                self.pc += 2
        elif (opcode & 0xF000) == 0x4000:  # 4xnn: Skip if Vx != nn
            if self.V[x] != nn:
                self.pc += 2
        elif (opcode & 0xF000) == 0x5000:  # 5xy0: Skip if Vx == Vy
            if self.V[x] == self.V[y]:
                self.pc += 2
        elif (opcode & 0xF000) == 0x6000:  # 6xnn: Vx = nn
            self.V[x] = nn
        elif (opcode & 0xF000) == 0x7000:  # 7xnn: Vx += nn
            self.V[x] = (self.V[x] + nn) & 0xFF
        elif (opcode & 0xF000) == 0x8000:  # 8xyn: ALU operations
            if n == 0x0:  # Vx = Vy
                self.V[x] = self.V[y]
            elif n == 0x1:  # Vx |= Vy
                self.V[x] |= self.V[y]
            elif n == 0x2:  # Vx &= Vy
                self.V[x] &= self.V[y]
            elif n == 0x3:  # Vx ^= Vy
                self.V[x] ^= self.V[y]
            elif n == 0x4:  # Vx += Vy
                result = self.V[x] + self.V[y]
                self.V[0xF] = 1 if result > 0xFF else 0
                self.V[x] = result & 0xFF
            elif n == 0x5:  # Vx -= Vy
                self.V[0xF] = 1 if self.V[x] >= self.V[y] else 0
                self.V[x] = (self.V[x] - self.V[y]) & 0xFF
            elif n == 0x6:  # Vx >>= 1
                self.V[0xF] = self.V[x] & 0x1
                self.V[x] >>= 1
            elif n == 0x7:  # Vx = Vy - Vx
                self.V[0xF] = 1 if self.V[y] >= self.V[x] else 0
                self.V[x] = (self.V[y] - self.V[x]) & 0xFF
            elif n == 0xE:  # Vx <<= 1
                self.V[0xF] = (self.V[x] & 0x80) >> 7
                self.V[x] = (self.V[x] << 1) & 0xFF
        elif (opcode & 0xF000) == 0x9000:  # 9xy0: Skip if Vx != Vy
            if self.V[x] != self.V[y]:
                self.pc += 2
        elif (opcode & 0xF000) == 0xA000:  # Annn: I = nnn
            self.I = nnn
        elif (opcode & 0xF000) == 0xB000:  # Bnnn: Jump to V0 + nnn
            self.pc = nnn + self.V[0]
        elif (opcode & 0xF000) == 0xC000:  # Cxnn: Vx = rand() & nn
            self.V[x] = random.randint(0, 255) & nn
        elif (opcode & 0xF000) == 0xD000:  # Dxyn: Draw sprite
            x_pos = self.V[x]
            y_pos = self.V[y]
            self.V[0xF] = 0
            for row in range(n):
                sprite_byte = self.memory[self.I + row]
                for col in range(8):
                    if (sprite_byte & (0x80 >> col)) != 0:
                        index = ((y_pos + row) % 32) * 64 + ((x_pos + col) % 64)
                        if self.display[index] == 1:
                            self.V[0xF] = 1
                        self.display[index] ^= 1
        elif (opcode & 0xF000) == 0xE000:
            if nn == 0x9E:  # Ex9E: Skip if key Vx pressed
                if self.keys[self.V[x]]:
                    self.pc += 2
            elif nn == 0xA1:  # ExA1: Skip if key Vx not pressed
                if not self.keys[self.V[x]]:
                    self.pc += 2
        elif (opcode & 0xF000) == 0xF000:
            if nn == 0x07:  # Fx07: Vx = delay timer
                self.V[x] = self.delay_timer
            elif nn == 0x0A:  # Fx0A: Wait for key press
                if not self.keys_pressed:
                    self.pc -= 2
                else:
                    self.V[x] = min(self.keys_pressed)
            elif nn == 0x15:  # Fx15: delay timer = Vx
                self.delay_timer = self.V[x]
            elif nn == 0x18:  # Fx18: sound timer = Vx
                self.sound_timer = self.V[x]
            elif nn == 0x1E:  # Fx1E: I += Vx
                self.I = (self.I + self.V[x]) & 0xFFF
            elif nn == 0x29:  # Fx29: I = sprite addr for Vx
                self.I = self.V[x] * 5
            elif nn == 0x33:  # Fx33: Store BCD of Vx
                self.memory[self.I] = self.V[x] // 100
                self.memory[self.I + 1] = (self.V[x] // 10) % 10
                self.memory[self.I + 2] = self.V[x] % 10
            elif nn == 0x55:  # Fx55: Save V0-Vx
                for i in range(x + 1):
                    self.memory[self.I + i] = self.V[i]
            elif nn == 0x65:  # Fx65: Load V0-Vx
                for i in range(x + 1):
                    self.V[i] = self.memory[self.I + i]

    def update_timers(self):
        # Update delay and sound timers
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def render(self):
        # Update rectangle visibility based on display state
        self.window.clear()
        pixels_on = sum(1 for pixel in self.display if pixel)
        logger.debug(f'Rendering display - Active pixels: {pixels_on}')
        for i, pixel in enumerate(self.display):
            self.rectangles[i].visible = bool(pixel)
        self.batch.draw()

    def test_display(self):
        # Fill the display with a test pattern for debugging
        for y in range(32):
            for x in range(64):
                self.display[y * 64 + x] = (x + y) % 2  # Checkerboard pattern
        self.batch.draw()

    def on_key_press(self, symbol, modifiers):
        # Map key presses to Chip-8 keypad
        key_map = {
            key._1: 0x1, key._2: 0x2, key._3: 0x3, key._4: 0xC,
            key.Q: 0x4, key.W: 0x5, key.E: 0x6, key.R: 0xD,
            key.A: 0x7, key.S: 0x8, key.D: 0x9, key.F: 0xE,
            key.Z: 0xA, key.X: 0x0, key.C: 0xB, key.V: 0xF
        }
        if symbol in key_map:
            self.keys[key_map[symbol]] = 1
            self.keys_pressed.add(key_map[symbol])
            logger.debug(f'Key pressed: 0x{key_map[symbol]:X}')

    def on_key_release(self, symbol, modifiers):
        # Map key releases to Chip-8 keypad
        key_map = {
            key._1: 0x1, key._2: 0x2, key._3: 0x3, key._4: 0xC,
            key.Q: 0x4, key.W: 0x5, key.E: 0x6, key.R: 0xD,
            key.A: 0x7, key.S: 0x8, key.D: 0x9, key.F: 0xE,
            key.Z: 0xA, key.X: 0x0, key.C: 0xB, key.V: 0xF
        }
        if symbol in key_map:
            self.keys[key_map[symbol]] = 0
            self.keys_pressed.discard(key_map[symbol])

    def run(self):
        logger.info('Starting CHIP-8 emulator')
        # Main emulation loop
        def update(dt):
            self.emulate_cycle()
            self.update_timers()
            self.render()

        pyglet.clock.schedule_interval(update, 1 / 60.0)  # Run at 60Hz
        pyglet.app.run()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("No ROM file specified")
        print("Usage: python main.py <ROM file>")
        sys.exit(1)

    rom_path = sys.argv[1]
    logger.info('Initializing CHIP-8 emulator')
    chip8 = Chip8()
    chip8.load_rom(rom_path)
    chip8.run()