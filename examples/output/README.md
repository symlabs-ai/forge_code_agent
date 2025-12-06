# Tetris

This is a classic Tetris game implemented in Python using the Pygame library.

## How to Play

1.  **Install Pygame:**
    ```bash
    pip install pygame
    ```

2.  **Run the game:**
    ```bash
    python tetris.py
    ```

3.  **Game Controls:**
    *   **Left Arrow:** Move the piece to the left.
    *   **Right Arrow:** Move the piece to the right.
    *   **Down Arrow:** Move the piece down faster.
    *   **Up Arrow:** Rotate the piece.

## Adding Sound Effects

This game comes with placeholders for sound effects. To add your own sounds, you will need to:

1.  Create a `sounds` folder in the same directory as `tetris.py`.
2.  Find or create your own sound files in `.wav` format.
3.  Name your sound files as follows:
    *   `rotate.wav`
    *   `move.wav`
    *   `drop.wav`
    *   `clear.wav`
    *   `game_over.wav`
4.  Uncomment the sound-related lines in the `tetris.py` file. You can find them by searching for the comment `# Sound effects`.
