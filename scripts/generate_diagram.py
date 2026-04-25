#!/usr/bin/env python3
"""Generate the VibeFinderAI 2.0 system architecture diagram.

Output: assets/architecture.png
Usage:  python scripts/generate_diagram.py
"""

from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # headless backend — no display needed
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

# ── layout ────────────────────────────────────────────────────────────────────

FIG_W, FIG_H = 24, 10

BOX_W = 3.0
BOX_H = 1.6

MAIN_Y = 7.0        # y-centre of the main left-to-right row
FALLBACK_Y = 3.6    # y-centre of the fallback box (below Gemini)

H_GAP = 0.55        # horizontal gap between adjacent main boxes
LEFT_MARGIN = 1.15  # x of the left edge of the first box

# Compute x-centres once
_STEP = BOX_W + H_GAP
xs = [LEFT_MARGIN + i * _STEP + BOX_W / 2 for i in range(6)]

# ── content ──────────────────────────────────────────────────────────────────

MAIN_LABELS = [
    "User\nNatural Language\nQuery",
    "RAG Retriever\n(sentence-\ntransformers)",
    "Top-K\nCandidates",
    "Gemini AI Agent\n(google-\ngenerativeai)",
    "Recommendations\n+ Explanations\n+ Confidence Scores",
    "Session Logger\nlogs/session.log",
]

# Italic captions rendered below specific boxes (index → text)
SUB_LABELS = {
    1: "songs.csv embeddings",
    3: "reasoning + confidence",
}

# Blue → teal → green progression; slate for the logger
MAIN_COLORS = [
    "#1565C0",  # deep blue      User
    "#0277BD",  # medium blue    RAG Retriever
    "#0097A7",  # cyan-teal      Top-K Candidates
    "#00695C",  # dark teal      Gemini AI Agent
    "#2E7D32",  # green          Recommendations
    "#455A64",  # blue-grey      Session Logger
]

FALLBACK_COLOR = "#B71C1C"   # deep red
FALLBACK_ARROW_COLOR = "#E53935"
MAIN_ARROW_COLOR = "#546E7A"
TEXT_COLOR = "white"


# ── drawing helpers ───────────────────────────────────────────────────────────

def _box(ax, cx, cy, label, color, fontsize=9.5):
    """Draw a rounded rectangle centred on (cx, cy) with multi-line label."""
    patch = FancyBboxPatch(
        (cx - BOX_W / 2, cy - BOX_H / 2),
        BOX_W, BOX_H,
        boxstyle="round,pad=0.13",
        facecolor=color,
        edgecolor="white",
        linewidth=2.0,
        zorder=3,
    )
    ax.add_patch(patch)
    ax.text(
        cx, cy, label,
        ha="center", va="center",
        color=TEXT_COLOR, fontsize=fontsize,
        fontweight="bold", linespacing=1.5,
        zorder=4,
    )


def _h_arrow(ax, x_start, x_end, y, color=MAIN_ARROW_COLOR, lw=2.0):
    """Solid horizontal arrow."""
    ax.annotate(
        "", xy=(x_end, y), xytext=(x_start, y),
        arrowprops=dict(arrowstyle="->", color=color, lw=lw),
        zorder=2,
    )


def _dashed_v_arrow(ax, x, y_start, y_end, color=FALLBACK_ARROW_COLOR, lw=2.2):
    """Dashed vertical arrow (down)."""
    patch = FancyArrowPatch(
        (x, y_start), (x, y_end),
        arrowstyle="->",
        mutation_scale=20,
        linestyle="dashed",
        color=color,
        linewidth=lw,
        zorder=2,
    )
    ax.add_patch(patch)


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    out = Path("assets/architecture.png")
    out.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.set_xlim(0, FIG_W)
    ax.set_ylim(0, FIG_H)
    ax.axis("off")

    # ── diagram title ─────────────────────────────────────────────────────────
    ax.text(
        FIG_W / 2, FIG_H - 0.45,
        "VibeFinderAI 2.0 — System Architecture",
        ha="center", va="top",
        fontsize=15, fontweight="bold", color="#1A237E",
    )

    # ── main row: boxes + arrows + sub-labels ─────────────────────────────────
    for i, (cx, label, color) in enumerate(zip(xs, MAIN_LABELS, MAIN_COLORS)):
        _box(ax, cx, MAIN_Y, label, color)

        # Sub-label below the box (italic caption)
        if i in SUB_LABELS:
            ax.text(
                cx, MAIN_Y - BOX_H / 2 - 0.22,
                SUB_LABELS[i],
                ha="center", va="top",
                color=color, fontsize=8.5, style="italic",
            )

        # Arrow to the next box
        if i < len(xs) - 1:
            _h_arrow(
                ax,
                cx + BOX_W / 2,
                xs[i + 1] - BOX_W / 2,
                MAIN_Y,
            )

    # ── fallback box ──────────────────────────────────────────────────────────
    gemini_cx = xs[3]
    _box(ax, gemini_cx, FALLBACK_Y, "Rule-Based Fallback\n(top-3 scorer)",
         FALLBACK_COLOR)

    # ── dashed arrow: Gemini ↓ Fallback ──────────────────────────────────────
    # Offset slightly left so the arrow doesn't run through the "reasoning +
    # confidence" sub-label that sits centred below the Gemini box.
    arrow_x = gemini_cx - 0.65
    arrow_y_top = MAIN_Y - BOX_H / 2        # bottom edge of Gemini box
    arrow_y_bot = FALLBACK_Y + BOX_H / 2    # top edge of Fallback box

    _dashed_v_arrow(ax, arrow_x, arrow_y_top, arrow_y_bot)

    # "on error" label to the left of the dashed arrow
    mid_y = (arrow_y_top + arrow_y_bot) / 2
    ax.text(
        arrow_x - 0.18, mid_y, "on error",
        ha="right", va="center",
        color=FALLBACK_ARROW_COLOR, fontsize=9.5, fontweight="bold",
    )

    # ── legend strip at the bottom ────────────────────────────────────────────
    legend_y = 0.72
    ax.plot([1.2, 3.2], [legend_y, legend_y],
            color=MAIN_ARROW_COLOR, lw=2, solid_capstyle="round")
    ax.annotate("", xy=(3.2, legend_y), xytext=(3.0, legend_y),
                arrowprops=dict(arrowstyle="->", color=MAIN_ARROW_COLOR, lw=2))
    ax.text(3.4, legend_y, "primary flow", va="center", fontsize=9, color="#37474F")

    ax.plot([6.5, 8.5], [legend_y, legend_y],
            color=FALLBACK_ARROW_COLOR, lw=2, linestyle="dashed")
    ax.annotate("", xy=(8.5, legend_y), xytext=(8.3, legend_y),
                arrowprops=dict(arrowstyle="->", color=FALLBACK_ARROW_COLOR, lw=2))
    ax.text(8.7, legend_y, "fallback path (on Gemini error)",
            va="center", fontsize=9, color="#37474F")

    # ── save ─────────────────────────────────────────────────────────────────
    plt.savefig(str(out), dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    size_kb = out.stat().st_size // 1024
    print(f"Saved {out}  ({size_kb} KB)")


if __name__ == "__main__":
    main()
