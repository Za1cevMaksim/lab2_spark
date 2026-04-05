import json
import matplotlib.pyplot as plt

with open("final_results.json") as f:
    data = json.load(f)

labels = ["1DN Base", "1DN Opt", "3DN Base", "3DN Opt"]
times = [d["time_sec"] for d in data]
rams  = [d["ram_mb"] for d in data]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
colors = ["#ff6b6b", "#4ecdc4", "#ffe66d", "#95e1d3"]

ax1.bar(labels, times, color=colors)
ax1.set_ylabel("Время (сек)")
ax1.set_title("Скорость выполнения")
for i, v in enumerate(times):
    ax1.text(i, v + 0.5, f"{v:.2f}s", ha='center', fontweight='bold')

ax2.bar(labels, rams, color=colors)
ax2.set_ylabel("RAM (MB)")
ax2.set_title("Пиковое потребление памяти")
for i, v in enumerate(rams):
    ax2.text(i, v + 5, f"{v:.2f}MB", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig("lab2_results.png", dpi=300)
plt.show()