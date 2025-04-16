import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import mplcursors
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle
from PIL import Image
import os

plt.style.use('seaborn-v0_8-whitegrid')

# Load and preprocess
df = pd.read_csv("notebooks/data/complete/ticket_sales.csv")
df_filtered = df[df["Price Category"] == "Stehplatz"].copy()
df_filtered["Booked Tickets"] = pd.to_numeric(df_filtered["Booked Tickets"], errors="coerce")
df_filtered["AVG Price"] = pd.to_numeric(df_filtered["AVG Price"], errors="coerce")
df_filtered = df_filtered.dropna(subset=["Booked Tickets", "AVG Price"])

# Extract opponent and compute revenue
df_filtered["Opponent"] = df_filtered["EventName"].str.split(" vs. ").str[1]
df_filtered["Opponent"] = df_filtered["Opponent"].replace({"1. FC Heidenheim": "1. FC Heidenheim 1846"})
df_filtered["Revenue"] = df_filtered["AVG Price"] * df_filtered["Booked Tickets"]

# Filter relevant competition
df_competition = df_filtered[df_filtered["Competition"].str.startswith("Bundesliga")].copy()

# Aggregate statistics
avg_tickets = df_competition.groupby("Opponent", as_index=False)["Booked Tickets"].mean()
avg_price = df_competition.groupby("Opponent", as_index=False)["AVG Price"].mean()
avg_revenue = df_competition.groupby("Opponent", as_index=False)["Revenue"].mean()

df_agg = pd.merge(avg_tickets, avg_price, on="Opponent")
df_agg = pd.merge(df_agg, avg_revenue, on="Opponent")
df_agg = df_agg.sort_values("Revenue", ascending=False)

# Setup color and size mapping
opponent_colors = {opp: color for opp, color in zip(df_agg["Opponent"], plt.cm.tab20(np.linspace(0, 1, len(df_agg))))}
size_min, size_max = 60, 350
norm_revenue = (df_agg['Revenue'] - df_agg['Revenue'].min()) / (df_agg['Revenue'].max() - df_agg['Revenue'].min())
bubble_sizes = size_min + norm_revenue * (size_max - size_min)

# Plot
fig, ax = plt.subplots(figsize=(14, 7), dpi=100, facecolor='white')
ax.set_xlim(df_agg["AVG Price"].min() * 0.95, df_agg["AVG Price"].max() * 1.05)
ax.set_ylim(df_agg["Booked Tickets"].min() * 0.95, df_agg["Booked Tickets"].max() * 1.05)

for _, row in df_agg.iterrows():
    ax.scatter(
        row["AVG Price"],
        row["Booked Tickets"],
        s=size_min + (row["Revenue"] - df_agg["Revenue"].min()) / (df_agg["Revenue"].max() - df_agg["Revenue"].min()) * (size_max - size_min),
        color=opponent_colors[row["Opponent"]],
        alpha=0.7,
        edgecolor='white',
        linewidth=0.5
    )

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(0.5)
ax.spines['left'].set_linewidth(0.5)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'€{int(x)}' if x == int(x) else f'€{x:.1f}'))
ax.grid(True, linestyle='--', alpha=0.3)

ax.set_title("Correlations Between Ticket Demand and Opponents", fontsize=14, weight='bold', pad=15, color='#232F3E')
ax.set_xlabel("Average Ticket Price", fontsize=11, weight='medium', color='#232F3E', labelpad=10)
ax.set_ylabel("Average Tickets Booked", fontsize=11, weight='medium', color='#232F3E', labelpad=10)

legend_items = [
    plt.Line2D([0], [0], marker='o', color='w',
               markerfacecolor=opponent_colors[row["Opponent"]],
               markersize=10,
               label=f"{row['Opponent']} (€{row['Revenue']:.0f})")
    for _, row in df_agg.iterrows()
]

ax.legend(handles=legend_items, loc='center left', bbox_to_anchor=(1.01, 0.5), fontsize=8,
          frameon=True, framealpha=0.7, edgecolor='lightgray', title="Opponents (Avg Revenue)", title_fontsize=10)

plt.figtext(0.75, 0.13,
            "Bubble size represents average revenue\n generated against each opponent",
            ha="center", fontsize=9, style='italic', color='#555555')

# Logos
logo_paths = ['aws.png', 'dfl.png', 'eintracht.jpg']
logo_positions = [[0.76, 0.89, 0.07, 0.07], [0.74, 0.9, 0.05, 0.05], [0.70, 0.9, 0.05, 0.05]]

for path, pos in zip(logo_paths, logo_positions):
    if os.path.exists(path):
        img = Image.open(path)
        ax_logo = fig.add_axes(pos, anchor='NE', zorder=1)
        ax_logo.imshow(np.array(img))
        ax_logo.axis('off')

plt.tight_layout(rect=[0, 0, 0.85, 0.95])
plt.savefig('bundesliga_ticket_analysis.png', dpi=300, bbox_inches='tight', transparent=False)
plt.show()
