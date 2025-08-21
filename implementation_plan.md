# Implementation Plan: Muse‑Pong (Muse 

# Blink‑Controlled Pong)

**EEG Blink Detection Feasibility:** The Muse 2 headband has four EEG electrodes (TP9, AF7, AF8, TP10 at
256 Hz) and even reports _“Blink”_ markers in its data stream. This means hardware is in place to
sense blinks. Prior research confirms that eye‑blink artifacts in Muse EEG are strong and easily detected
with simple methods. For example, a Muse‑based blink detector using only deterministic signal processing
(no ML) achieved 100% accuracy on its dataset , and other peak‑threshold methods on EEG report ≈98–
99% accuracy. In short, using Muse  2 to detect blinks is **feasible** : blinks produce large frontal EEG
deflections that can be captured by the headband and identified reliably.

**Threshold vs. ML:** Complex ML is **not required** for simple blink detection. The cited studies above used
_non‑learning, threshold_ algorithms to spot blink peaks. In practice, one can bandpass‑filter the raw
EEG (e.g. 1–10 Hz) or compute band powers and then apply a peak or threshold rule (e.g. sudden jump in
delta or drop in alpha) to flag blinks. Thresholding is fast and works in real time, which is ideal for a
lightweight MVP. (ML models would require collecting blink training data and run inference, adding latency.)
In fact, hobbyist projects have simply watched the Muse output (or derived band‐powers) and printed
“blink” when values exceed a preset cutoff. A simple example: if the recent _Delta_ and _Theta_ power rise
above thresholds while _Alpha_ stays low, treat that as a blink. This approach is deterministic, robust, and
avoids ML complexity.

**Pyimgui for 2D Pong:** The pyimgui library (a Python wrapper for Dear ImGui) can be used to render a
simple 2D Pong game. Pyimgui is an _immediate‑mode GUI_ toolkit that supports custom drawing commands.
It integrates with game frameworks like Pygame (via imgui.integrations.pygame). We can use its
drawing API to draw shapes: for instance, draw_list.add_rect_filled(x1,y1,x2,y2,color) draws
a filled rectangle. In practice, one would create an ImGui window or canvas and draw two paddle
rectangles and a ball (circle or small rect) each frame. This is very lightweight (no heavy graphics pipeline)
and works on desktop. In summary, pyimgui provides immediate‐mode drawing and event loops suitable
for a quick Pong prototype.

**Implementation Outline:** Based on the above, the plan is:

```
Stream EEG from Muse 2: Use an LSL inlet to read Muse EEG (or BrainFlow). For example, using the
given LSL code snippet, we resolve the EEG stream and start pulling chunks in a loop (as shown in
the provided code).
```
```
# Example: connect to Muse via LSL (assuming Bluemuse or MuseLSL is
running)
frompylslimport StreamInlet, resolve_byprop
print("Looking for an EEG stream...")
streams= resolve_byprop('type', 'EEG', timeout=5)
```
```
1 2
```
```
3
4
3 4
```
```
3 4
```
```
5
```
```
3 4
```
```
6
```
```
7
```
```
6 7
```
## 1.


```
ifnot streams: raise RuntimeError("No EEG stream found")
inlet= StreamInlet(streams[0])
fs = int(inlet.info().nominal_srate()) # should be 256 Hz for Muse 2
```
```
Detect Blinks via Thresholding: In the data loop, compute a simple metric and apply a threshold.
For instance, compute band powers (alpha, delta) using a short FFT window (as in the example), then
check if Delta > δ_thresh and Alpha < α_thresh. A single if‑statement can then fire a “blink” event
without ML. For example:
```
```
# Inside the data acquisition loop:
eeg_data, timestamp = inlet.pull_chunk(timeout=1, max_samples=int(0.5*fs))
ifnot eeg_data: continue
# Preprocess: bandpass filter, etc. Then compute band powers (using
provided utils or np.fft).
band_powers = utils.compute_band_powers(eeg_data, fs)
delta, theta, alpha, beta = band_powers
# Simple blink condition:
ifdelta> 2.0 andalpha < 1.0:
blink = True
else:
blink = False
# (Tweak thresholds via trial; above is just illustrative.)
ifblink:
print("Blink detected!") # or trigger game action
```
```
This leverages the fact that a blink produces a large positive deflection (captured in delta/theta) and
relatively low alpha. Fine‑tuning or additional smoothing can reduce false positives, but no
training is needed.
```
```
Pong Game Loop (pyimgui): Use pyimgui (with a simple backend like GLFW or Pygame) to create a
window and draw the game each frame. Initialize ImGui and a renderer, then in the main loop:
handle OS events, start a new ImGui frame, draw paddles/ball, end the frame, and render. For
example:
```
```
import imgui
fromimgui.integrations.pygameimport PygameRenderer
import pygame
```
```
pygame.init()
size= 640, 480
screen = pygame.display.set_mode(size, pygame.DOUBLEBUF| pygame.OPENGL |
pygame.RESIZABLE)
imgui.create_context()
impl= PygameRenderer()
paddle_x, paddle_y= 50, 200 # initial position of player paddle
```
## 2.

```
3 5
```
## 3.


```
ball_x, ball_y = 320, 240 # initial ball position
# Main loop:
running= True
whilerunning:
for eventin pygame.event.get():
ifevent.type == pygame.QUIT:
running= False
impl.process_event(event)
impl.process_inputs()
imgui.new_frame()
# Game logic: e.g., move ball
ball_x += 2; ball_y += 1 # simple movement example
# Draw paddles and ball as rectangles:
draw= imgui.get_window_draw_list()
# Draw player paddle:
draw.add_rect_filled(paddle_x, paddle_y, paddle_x+10, paddle_y+80,
imgui.get_color_u32_rgba(1,1,1,1))
# Draw opponent paddle and ball similarly...
draw.add_rect_filled(ball_x, ball_y, ball_x+10, ball_y+10,
imgui.get_color_u32_rgba(1,1,1,1))
imgui.render()
impl.render(imgui.get_draw_data())
pygame.display.flip()
```
```
Here, add_rect_filled draws simple white rectangles for paddles and the ball. You can
adjust positions each frame (e.g. moving the player paddle up/down when a blink is detected).
Pyimgui takes care of rendering with OpenGL under the hood.
```
```
Mapping Blink to Control: In the loop above, integrate the blink detection. For example, whenever
blink == True from step 2, change paddle_y (e.g. move up or down). You might debounce so
one blink equals one move. For instance:
```
```
# Inside loop after detecting 'blink':
ifblink:
paddle_y -= 20 # move paddle up on blink (example)
# Ensure paddle_y stays in bounds of the window
paddle_y= max(0, min(paddle_y, size[1]-80))
```
```
This ties the EEG input to the game: each detected blink shifts the paddle. Over time, one can refine
to support “flapping” style movement (if trying a Flappy‑Bird variant) or toggling direction.
```
```
Additional Games: Once the infrastructure is in place (Muse stream + blink detection + pyimgui
loop), adding new game environments is straightforward. You can redraw different scenes with
ImGui commands. For example, a Flappy‑Bird clone could draw a circle (the bird) and move it
vertically on blinks, with pipes as rectangles. The same blink thresholds apply.
```
```
7
```
## 4.

## 5.


In summary, **no heavy ML is needed** – simple thresholding (and optional smoothing) suffices to flag blinks
in real time. The Muse 2’s EEG output and built‑in markers confirm blinks are well within reach

. Pyimgui provides the rendering layer for a 2D game with minimal overhead. By combining
these, a basic MVP Muse‑Pong can be built with straightforward Python code as sketched above.

**Sources:** Muse 2 specs and documentation ; EEG blink‑detection literature ; pyimgui
documentation.

Muse 2 Specifications - Final Version.docx
https://ifelldh.tec.mx/sites/g/files/vgjovo1101/files/Muse%202%20Specifications.pdf

isip.piconepress.com
https://isip.piconepress.com/conferences/ieee_spmb/2022/papers/l01_03.pdf

ej-eng.org
https://ej-eng.org/index.php/ejeng/article/download/2438/1089/

Using blinks to speak. Using the Muse headband to type words... | by Daniel G | Medium
https://medium.com/@daniel2023g/using-blinks-to-speak-759f0c0d46de

First steps with imgui — pyimgui 2.0.0 documentation
https://pyimgui.readthedocs.io/en/latest/guide/first-steps.html

imgui.core module — pyimgui 2.0.0 documentation
https://pyimgui.readthedocs.io/en/latest/reference/imgui.core.html

```
3 4 1
2 6 7
```
```
1 2 3 4
6 7
```
```
1 2
```
```
3
```
```
4
```
```
5
```
```
6
```
```
7
```

