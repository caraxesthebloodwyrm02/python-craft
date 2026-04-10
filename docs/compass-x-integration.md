# Compass, graph paper, and the integration X (entry level)

**Audience:** high school / first-year technical readers  
**Idea:** Two parallel “rails” (grounded bodies) and a honest compass construction locate a **center**; from that center, symmetric gestures define a pair of lines that read visually as **`/`** and **`\`**, crossing in an **X**. The crossing is the **integration point**—the third structure that appears only once the first two are fixed and related by construction.

---

## 1. Basic practices (compass + pencil + geometry graph paper)

| Practice | Why it matters |
| --- | --- |
| **Flat surface, sharp pencil** | A dull point widens intersections; arcs wobble. |
| **Plant the compass needle firmly** | Slip moves every downstream intersection. |
| **Do not change the compass opening mid-step** | Each construction step is a logical promise; changing radius breaks the proof. |
| **Use the grid for alignment, not as a shortcut** | Graph paper helps you keep parallels straight and spot symmetry; classical constructions use compass + straightedge logic—use the ruler only as an unmarked straightedge unless the exercise allows measurement. |
| **Label points as you go** (`A`, `B`, `O`, `P`, …) | You are building a **chain of reasoning**; unnamed points are lost infrastructure. |
| **Light construction lines first; ink or bold last** | Erase/refine without destroying the work. |
| **Rotate the paper** | Comfort beats torque; accuracy follows a stable wrist. |
| **Check mentally** | Parallel lines stay parallel; a perpendicular bisector meets a segment at its midpoint at 90°. |

**Curves on paper:** A compass draws **circles and arcs** (parts of circles), not freehand “curves.” Smooth circles come from **continuous rotation** of the handle while the needle stays fixed. For this document, “gesture” means **swing a well-chosen arc**—the arc’s intersections with lines or other arcs are the **points of relevance**.

---

## 2. Infrastructure map (what each object means)

| Object | Role |
| --- | --- |
| **Two parallel lines** | Two **parallel bodies**—same direction, never meeting; they define a **strip** of space between them. |
| **Perpendicular segment between them** | **Grounding**: ties the two parallels with shortest bridge; its **midpoint** is equidistant from both. |
| **Compass arcs from that midpoint** | **Centering**: the construction forces a point that does not favor either parallel. |
| **Bisected right angle at the center** | Produces two lines through the center at **45°** to the grid rails—visually **`/`** and **`\`**. |
| **The X** | The two lines meet only at the **integration point**—the **third body** (the cross) is defined by the first two plus the construction. |

---

## 3. Hands-on procedure (paper)

**Given:** two horizontal parallel lines on graph paper (use two separate grid rows), far enough apart to swing arcs comfortably.

1. **Anchor** — Pick point `A` on the upper line and `B` on the lower line in the **same column** (same \(x\) on the grid). Segment `AB` is perpendicular to both parallels.
2. **Bisect `AB`** — With compass, draw equal-radius arcs from `A` and `B` so they meet on both sides of `AB`; draw the line through those two arc meetings. It hits `AB` at **`O`**, the **midpoint** (equidistant from both parallels). **`O` is the integration center** for this setup.
3. **Right angle at `O`** — Through `O`, construct a line **perpendicular** to `AB` (along the parallels’ direction). On graph paper, `AB` is vertical, so this is the **horizontal through `O`** (still verify with construction if you are doing pure classical work).
4. **Split the right angle into two 45° rays** — Bisect the 90° angle at `O` formed by the horizontal through `O` and one perpendicular to the parallels (standard angle-bisector construction with compass). The two bisector rays point along diagonals: one reads as **`/`**, one as **`\`** when you trace them across the strip.
5. **Draw the X** — With straightedge, draw both rays through `O` across your diagram. Their intersection is **`O`**; the **shape X** is the pair of lines, not a filled region.

**Takeaway:** The two parallels alone do not contain a unique “middle”; **grounding** (`AB`) plus **bisection** creates **`O`**. The **diagonal pair** is then **forced** by symmetry, not guessed.

---

## 4. Executive code: points of relevance per step

Coordinates are on a square grid: \(x\) right, \(y\) up. Parallel bodies are horizontal lines \(y = y_1\) and \(y = y_2\).

### Step 0 — Define the two parallel bodies (rails)

```python
# Two parallel horizontal lines (infrastructure rails)
y_top, y_bottom = 6.0, 2.0
# All points on upper rail share y_top; lower rail shares y_bottom.
```

### Step 1 — Grounding segment AB (same column)

```python
x_a = 4.0
A = (x_a, y_top)
B = (x_a, y_bottom)
# AB is perpendicular to both rails.
```

### Step 2 — Integration center O (midpoint = perpendicular bisector foot on AB)

```python
O = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
# O is equidistant from both rails; distance to each rail is |y_top - y_bottom| / 2.
```

### Step 3 — Horizontal through O (parallel to the rails, through the center)

```python
# Line H: y = O[1]  (infinite line conceptually; pick two points for drawing)
H_left, H_right = (O[0] - 5.0, O[1]), (O[0] + 5.0, O[1])
```

### Step 4 — Directions for "/" and "\" (45° through O)

```python
import math

def diagonal_through(O, theta_deg: float, length: float = 8.0):
    """Two points on opposite sides of O along direction theta (from +x axis)."""
    t = math.radians(theta_deg)
    dx, dy = math.cos(t), math.sin(t)
    return (O[0] - length * dx, O[1] - length * dy), (O[0] + length * dx, O[1] + length * dy)

# One diagonal (e.g. rising like /): 45°
P_neg, P_pos = diagonal_through(O, 45.0)
# The other diagonal (like \): 135° (or -45°)
Q_neg, Q_pos = diagonal_through(O, 135.0)
```

### Step 5 — Verify: single intersection (the X’s center)

```python
def line_intersection(a1, a2, b1, b2):
    """Return intersection of infinite lines a1-a2 and b1-b2, or None if parallel."""
    x1, y1 = a1
    x2, y2 = a2
    x3, y3 = b1
    x4, y4 = b2
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-9:
        return None
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
    return px, py

X_center = line_intersection(P_neg, P_pos, Q_neg, Q_pos)
assert X_center is not None
assert abs(X_center[0] - O[0]) < 1e-9 and abs(X_center[1] - O[1]) < 1e-9
```

### Step 6 — Optional: compass arc locus (same center `O`, radius r)

```python
import math

def arc_points(O, r: float, start_deg: float, end_deg: float, n: int = 72):
    """Sample points on an arc for plotting or CNC-style output."""
    out = []
    for i in range(n + 1):
        u = i / n
        th = math.radians(start_deg + u * (end_deg - start_deg))
        out.append((O[0] + r * math.cos(th), O[1] + r * math.sin(th)))
    return out

# Example: semicircle opening "between" the rails
arc = arc_points(O, r=3.0, start_deg=0.0, end_deg=180.0)
```

---

## 5. One-block runner (copy-paste)

```python
import math

y_top, y_bottom = 6.0, 2.0
x_a = 4.0
A, B = (x_a, y_top), (x_a, y_bottom)
O = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)

def diagonal_through(O, theta_deg, length=8.0):
    t = math.radians(theta_deg)
    dx, dy = math.cos(t), math.sin(t)
    return (O[0] - length * dx, O[1] - length * dy), (O[0] + length * dx, O[1] + length * dy)

slash_fwd = diagonal_through(O, 45.0)    # reads like /
slash_back = diagonal_through(O, 135.0)  # reads like \

print("Rails: y =", y_top, "and y =", y_bottom)
print("Grounding A, B:", A, B)
print("Integration center O:", O)
print("Diagonal / :", slash_fwd)
print("Diagonal \\ :", slash_back)
```

---

## 6. Closing metaphor (precision without mystique)

- **Parallel bodies** alone do not pick a unique “between” point in the infinite strip.  
- **Grounding** (a perpendicular bridge `AB`) turns “between” into a **segment**.  
- **Bisection** turns that segment into a **unique center** `O`.  
- **Compass gestures** (arcs obeying fixed radii) are how you **prove** you are at that center, not eyeballing it.  
- The **`/`** and **`\`** pair is then a **symmetric completion**: the **X** marks where both diagonals agree—the **ultra-precise third structure** is the **relation** (the cross), whose only finite meeting point is **`O`**.

---

## References (general level)

- High school geometry curricula typically include compass-and-straightedge constructions: perpendicular bisector, angle bisector, perpendicular through a point, parallel through a point.  
- Graph paper is used widely to support alignment and verification while students learn the logical sequence of steps (see standard geometry texts and state standards for **Geometric Constructions**).

*This note is instructional; it mixes classical ideas with a coordinate picture so you can cross-check intersections numerically.*
