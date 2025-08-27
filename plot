import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gaussian_kde

# --- Synthetic dataset ---
np.random.seed(42)
df = pd.DataFrame({
    "Category1": np.repeat(["A","B","C"], 200),
    "Category2": np.tile(np.repeat(["X","Y"], 100), 3),
    "Value": np.concatenate([
        np.random.normal(10, 2, 100),  # A-X
        np.random.normal(15, 2, 100),  # A-Y
        np.random.normal(20, 2, 100),  # B-X
        np.random.normal(25, 2, 100),  # B-Y
        np.random.normal(30, 2, 100),  # C-X
        np.random.normal(35, 2, 100),  # C-Y
    ])
})

# --- Ridgeline plot ---
fig, ax = plt.subplots(figsize=(8,6))
palette = sns.color_palette("Set2", len(df["Category2"].unique()))

categories = df["Category1"].unique()
cat2 = df["Category2"].unique()
x = np.linspace(df["Value"].min()-2, df["Value"].max()+2, 300)

for i, c1 in enumerate(categories):
    offset = i * 1.5
    for j, c2 in enumerate(cat2):
        subset = df[(df["Category1"] == c1) & (df["Category2"] == c2)]["Value"]
        kde = gaussian_kde(subset)
        y = kde(x)
        y = y / y.max()  # normalize height
        ax.fill_between(x, offset, y+offset, alpha=0.6, color=palette[j], label=c2 if i==0 else "")
        ax.plot(x, y+offset, color="k", lw=0.8)

ax.set_yticks([i*1.5 for i in range(len(categories))])
ax.set_yticklabels(categories)
ax.set_xlabel("Value")
ax.set_ylabel("Category1")
ax.legend(title="Category2", bbox_to_anchor=(1.05,1), loc="upper left")
plt.title("Ridgeline with rows=Category1 and colors=Category2")
plt.tight_layout()
plt.show()
