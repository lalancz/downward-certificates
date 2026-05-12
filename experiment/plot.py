import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('proof_sizes_rule.csv')

df['lmcut_proof_size_bytes'] = pd.to_numeric(df['lmcut_proof_size_bytes'], errors='coerce')
df['merge_and_shrink_proof_size_bytes'] = pd.to_numeric(df['merge_and_shrink_proof_size_bytes'], errors='coerce')

df_both = df.dropna(subset=['lmcut_proof_size_bytes', 'merge_and_shrink_proof_size_bytes'])
df_both = df_both[(df_both['lmcut_proof_size_bytes'] > 0) & (df_both['merge_and_shrink_proof_size_bytes'] > 0)]

df_lmcut_only = df[df['lmcut_proof_size_bytes'].notna() & df['merge_and_shrink_proof_size_bytes'].isna()]
df_lmcut_only = df_lmcut_only[df_lmcut_only['lmcut_proof_size_bytes'] > 0]

df_mas_only = df[df['lmcut_proof_size_bytes'].isna() & df['merge_and_shrink_proof_size_bytes'].notna()]
df_mas_only = df_mas_only[df_mas_only['merge_and_shrink_proof_size_bytes'] > 0]

fig, ax = plt.subplots(figsize=(11, 11))

min_val = 1e6
max_val = 1e0

x_both = df_both['lmcut_proof_size_bytes'].values
y_both = df_both['merge_and_shrink_proof_size_bytes'].values
min_val = min(min_val, x_both.min(), y_both.min())
max_val = max(max_val, x_both.max(), y_both.max())

max_val = max(max_val, df_lmcut_only['lmcut_proof_size_bytes'].max())

max_val = max(max_val, df_mas_only['merge_and_shrink_proof_size_bytes'].max())

plot_min = min_val * 0.5
plot_max = max_val * 1.5

ax.set_xlim(plot_min, plot_max)
ax.set_ylim(plot_min, plot_max)

x_both = df_both['lmcut_proof_size_bytes'].values
y_both = df_both['merge_and_shrink_proof_size_bytes'].values
ax.scatter(x_both, y_both, alpha=0.6, s=60, color='steelblue', 
            edgecolors='black', linewidth=0.5, label='Both heuristics')

x_lmcut = df_lmcut_only['lmcut_proof_size_bytes'].values
y_lmcut = np.full_like(x_lmcut, plot_max)
ax.scatter(x_lmcut, y_lmcut, alpha=0.6, s=60, color='steelblue', 
            edgecolors='black', linewidth=0.5, label='Both heuristics')

x_mas = np.full_like(df_mas_only['merge_and_shrink_proof_size_bytes'].values, plot_max)
y_mas = df_mas_only['merge_and_shrink_proof_size_bytes'].values
ax.scatter(x_mas, y_mas, alpha=0.6, s=60, color='steelblue', 
            edgecolors='black', linewidth=0.5, label='Both heuristics')

ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Parity (y=x)', alpha=0.7)

ax.set_xscale('log')
ax.set_yscale('log')

ax.grid(True, alpha=0.3)

ax.set_aspect('equal', adjustable='box')

ax.set_xlabel('LMCut Proof Size (bytes)', fontsize=12)
ax.set_ylabel('Merge and Shrink Proof Size (bytes)', fontsize=12)

plt.tight_layout()
plt.savefig('proof_sizes_parity.png', dpi=150)
print(f"Both heuristics succeeded: {len(df_both)}")
print(f"Only LMCut succeeded: {len(df_lmcut_only)}")
print(f"Only Merge and Shrink succeeded: {len(df_mas_only)}")
