"""
Generates two architecture diagrams for the SQLSpeak project and saves
them to the pic/ folder.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "pic")
os.makedirs(OUT_DIR, exist_ok=True)

# ── shared palette ────────────────────────────────────────────────────────────
C = {
    "ui":      "#3b82f6",   # blue  – Streamlit UI
    "agent":   "#8b5cf6",   # purple – agent layer
    "mcp":     "#10b981",   # green  – MCP layer
    "llm":     "#f59e0b",   # amber  – LLM providers
    "db":      "#ef4444",   # red    – Supabase / PostgreSQL
    "bg":      "#f8fafc",   # near-white background
    "border":  "#e2e8f0",
    "text":    "#1e293b",
    "subtext": "#64748b",
    "arrow":   "#94a3b8",
}


def box(ax, x, y, w, h, label, sublabel="", color="#ffffff", alpha=0.95,
        fontsize=11, subfontsize=8.5, radius=0.04):
    """Draw a rounded rectangle with a label and optional sublabel."""
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        linewidth=1.5, edgecolor=color, facecolor=color,
        alpha=alpha, zorder=3,
    )
    ax.add_patch(patch)
    # white inner fill
    inner = FancyBboxPatch(
        (x - w / 2 + 0.012, y - h / 2 + 0.012), w - 0.024, h - 0.024,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        linewidth=0, facecolor="white", alpha=0.92, zorder=4,
    )
    ax.add_patch(inner)
    cy = y if not sublabel else y + h * 0.12
    ax.text(x, cy, label, ha="center", va="center", fontsize=fontsize,
            fontweight="bold", color=C["text"], zorder=5)
    if sublabel:
        ax.text(x, y - h * 0.18, sublabel, ha="center", va="center",
                fontsize=subfontsize, color=C["subtext"], zorder=5,
                style="italic")


def arrow(ax, x0, y0, x1, y1, label="", color=None, lw=1.8,
          connectionstyle="arc3,rad=0.0", both=False):
    color = color or C["arrow"]
    style = "<->" if both else "->"
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(
                    arrowstyle=style, color=color, lw=lw,
                    connectionstyle=connectionstyle,
                ), zorder=2)
    if label:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        ax.text(mx, my + 0.035, label, ha="center", va="bottom",
                fontsize=7.5, color=C["subtext"], zorder=6,
                bbox=dict(fc="white", ec="none", pad=1))


# ══════════════════════════════════════════════════════════════════════════════
#  DIAGRAM 1 — Component Architecture
# ══════════════════════════════════════════════════════════════════════════════
def draw_architecture():
    fig, ax = plt.subplots(figsize=(13, 7.5))
    fig.patch.set_facecolor(C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    # ── title ─────────────────────────────────────────────────────────────
    ax.text(6.5, 7.1, "SQLSpeak — Component Architecture",
            ha="center", va="center", fontsize=15, fontweight="bold",
            color=C["text"])

    # ── layer labels (background bands) ───────────────────────────────────
    layers = [
        (0.3, 6.6, 1.8, "UI Layer",    C["ui"]),
        (0.3, 4.5, 1.8, "Agent Layer", C["agent"]),
        (0.3, 2.5, 1.8, "MCP Layer",   C["mcp"]),
        (0.3, 0.65, 1.8, "Database",   C["db"]),
    ]
    for lx, ly, lw, lt, lc in layers:
        rect = FancyBboxPatch((lx, ly - 0.45), lw, 0.75,
                              boxstyle="round,pad=0.0,rounding_size=0.06",
                              linewidth=0, facecolor=lc, alpha=0.12, zorder=1)
        ax.add_patch(rect)
        ax.text(lx + lw / 2, ly, lt, ha="center", va="center",
                fontsize=8, color=lc, fontweight="bold", zorder=2)

    # ── main column boxes ──────────────────────────────────────────────────
    #  col_x = 5.5  (main pipeline)
    #  col_x = 10.5 (LLM, off to the right)

    box(ax, 5.5, 6.6, 3.8, 0.72, "Streamlit UI", "main.py", C["ui"])
    box(ax, 5.5, 4.5, 3.8, 0.72, "SQLAgent", "agent/agent.py", C["agent"])
    box(ax, 5.5, 2.5, 3.8, 0.72, "MCP Client  +  ReAct Agent",
        "mcp_server/client.py  ·  LangGraph", C["mcp"])
    box(ax, 3.2, 0.65, 2.6, 0.72, "FastMCP Tool Server",
        "tools/supabase_tool.py", C["mcp"], alpha=0.75)
    box(ax, 7.8, 0.65, 2.6, 0.72, "Supabase PostgreSQL",
        "execute_sql() RPC", C["db"])

    # LLM box
    box(ax, 10.8, 2.5, 2.8, 0.72, "LLM Provider",
        "GPT-4o  /  Claude", C["llm"])

    # ── vertical arrows (main pipeline) ───────────────────────────────────
    arrow(ax, 5.5, 6.23, 5.5, 4.87, "user question / response",
          color=C["ui"], both=True)
    arrow(ax, 5.5, 4.13, 5.5, 2.87, "asyncio.run(agent_instance())",
          color=C["agent"])
    arrow(ax, 3.8, 2.13, 3.2, 1.02, "spawn subprocess\n(stdio)",
          color=C["mcp"])
    arrow(ax, 3.2, 1.02, 3.8, 2.13, "",
          color=C["mcp"])   # return arrow already drawn as both above

    # ── lateral arrows ─────────────────────────────────────────────────────
    # MCP client ↔ LLM
    arrow(ax, 7.4, 2.5, 9.4, 2.5, "tool calls / completions",
          color=C["llm"], both=True)

    # FastMCP tool server → Supabase
    arrow(ax, 4.5, 0.65, 6.5, 0.65, "supabase-py client",
          color=C["db"], both=True)

    # dotted "loads 4 tools" label between client and tool server
    ax.annotate("", xy=(4.5, 2.13), xytext=(3.5, 1.02),
                arrowprops=dict(arrowstyle="<-", color=C["mcp"], lw=1.5,
                                linestyle="dashed"), zorder=2)
    ax.text(3.6, 1.6, "loads 4 tools\nvia stdio", ha="center", va="center",
            fontsize=7.5, color=C["mcp"], style="italic")

    # ── legend ─────────────────────────────────────────────────────────────
    legend_items = [
        (C["ui"],    "UI / Streamlit"),
        (C["agent"], "Agent"),
        (C["mcp"],   "MCP layer"),
        (C["llm"],   "LLM providers"),
        (C["db"],    "Supabase / DB"),
    ]
    for i, (lc, lt) in enumerate(legend_items):
        lx = 9.5 + (i % 3) * 1.2
        ly = 6.6 - (i // 3) * 0.42
        ax.add_patch(plt.Rectangle((lx - 0.12, ly - 0.1), 0.22, 0.22,
                                   color=lc, alpha=0.8, zorder=5))
        ax.text(lx + 0.16, ly + 0.01, lt, va="center", fontsize=7.5,
                color=C["text"], zorder=5)

    plt.tight_layout(pad=0.3)
    out = os.path.join(OUT_DIR, "architecture.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=C["bg"])
    plt.close()
    print(f"Saved {out}")


# ══════════════════════════════════════════════════════════════════════════════
#  DIAGRAM 2 — Data Flow (single query lifecycle)
# ══════════════════════════════════════════════════════════════════════════════
def draw_data_flow():
    fig, ax = plt.subplots(figsize=(13, 8.5))
    fig.patch.set_facecolor(C["bg"])
    ax.set_facecolor(C["bg"])
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 8.5)
    ax.axis("off")

    ax.text(6.5, 8.1, "SQLSpeak — Data Flow per Query",
            ha="center", va="center", fontsize=15, fontweight="bold",
            color=C["text"])

    # Step definitions: (x, y, w, h, step_num, title, detail, color)
    steps = [
        (6.5, 7.3,  7.5, 0.65, "1", "User types a question",
         "Streamlit chat input  ·  main.py", C["ui"]),

        (6.5, 6.1,  7.5, 0.65, "2", "SQLAgent.run() called",
         "agent/agent.py  →  asyncio.run(agent_instance(...))", C["agent"]),

        (6.5, 4.95, 7.5, 0.65, "3", "MCP Client spawns supabase_tool.py subprocess",
         "mcp_server/client.py  ·  MultiServerMCPClient  ·  stdio transport", C["mcp"]),

        (6.5, 3.8,  7.5, 0.65, "4", "4 MCP tools loaded into LangGraph ReAct agent",
         "list_tables · get_table_schema · get_sample_rows · execute_sql", C["mcp"]),

        (6.5, 2.65, 7.5, 0.65, "5", "ReAct loop — LLM explores the database",
         "LLM calls tools in order  →  each tool hits Supabase via execute_sql() RPC", C["llm"]),

        (6.5, 1.5,  7.5, 0.65, "6", "LLM composes and executes the SQL",
         "LLM writes query  →  execute_sql(query)  →  Supabase returns rows", C["db"]),

        (6.5, 0.4,  7.5, 0.65, "7", "Answer returned to Streamlit chat",
         "SQL shown in code block  ·  results explained in plain English", C["ui"]),
    ]

    for (x, y, w, h, num, title, detail, color) in steps:
        # coloured left accent bar
        accent = FancyBboxPatch((x - w / 2, y - h / 2), 0.28, h,
                                boxstyle="round,pad=0.0,rounding_size=0.03",
                                linewidth=0, facecolor=color, alpha=0.85,
                                zorder=4)
        ax.add_patch(accent)

        # step box
        bg = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                            boxstyle="round,pad=0.0,rounding_size=0.04",
                            linewidth=1.2, edgecolor=color,
                            facecolor="white", alpha=0.95, zorder=3)
        ax.add_patch(bg)

        # step number
        ax.text(x - w / 2 + 0.14, y, num, ha="center", va="center",
                fontsize=13, fontweight="bold", color="white", zorder=5)

        # title
        ax.text(x - w / 2 + 0.42, y + 0.1, title,
                ha="left", va="center", fontsize=10.5,
                fontweight="bold", color=C["text"], zorder=5)

        # detail
        ax.text(x - w / 2 + 0.42, y - 0.13, detail,
                ha="left", va="center", fontsize=8,
                color=C["subtext"], zorder=5, style="italic")

        # connector arrow to next step
        if (x, y) != (steps[-1][0], steps[-1][1]):
            next_y = y - h / 2 - 0.05
            ax.annotate("", xy=(x, next_y - 0.21), xytext=(x, next_y),
                        arrowprops=dict(arrowstyle="-|>", color=color,
                                       lw=1.6), zorder=2)

    # ── side annotations (what happens at the DB side) ─────────────────────
    db_notes = [
        (5.0, "list_tables()\n→ information_schema.tables"),
        (3.8, "get_table_schema(t)\n→ information_schema.columns"),
        (2.65, "get_sample_rows(t)\n→ SELECT * LIMIT 5"),
        (1.5, "execute_sql(query)\n→ final result rows"),
    ]
    for ny, note in db_notes:
        ax.text(11.1, ny, note, ha="left", va="center", fontsize=7.2,
                color=C["db"],
                bbox=dict(fc="white", ec=C["db"], lw=0.8, pad=3,
                          boxstyle="round,pad=0.3"))
        ax.annotate("", xy=(10.25, ny), xytext=(11.05, ny),
                    arrowprops=dict(arrowstyle="<-", color=C["db"],
                                   lw=0.9, linestyle="dotted"), zorder=2)

    ax.text(11.8, 4.4, "Supabase\nPostgreSQL", ha="center", va="center",
            fontsize=9, fontweight="bold", color=C["db"],
            bbox=dict(fc=C["db"], ec=C["db"], alpha=0.12, pad=5,
                      boxstyle="round,pad=0.4"))

    plt.tight_layout(pad=0.3)
    out = os.path.join(OUT_DIR, "data_flow.png")
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=C["bg"])
    plt.close()
    print(f"Saved {out}")


if __name__ == "__main__":
    draw_architecture()
    draw_data_flow()
    print("Done.")
