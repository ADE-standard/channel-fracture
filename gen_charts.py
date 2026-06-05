"""Generate experiment comparison charts for Channel Fracture paper v2.
Light background, DejaVu Sans font, English annotations only."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

OUT = '/tmp/channel-fracture/experiments/visuals'
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 9,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#D1D5DB',
    'axes.grid': True,
    'grid.color': '#F3F4F6',
    'grid.alpha': 1.0,
})


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=200, bbox_inches='tight', facecolor='white')
    print(f'{name}: {os.path.getsize(path)} bytes')
    plt.close(fig)


# ─── T5: Concurrent Conflict Detection ───────────────────────────────
def chart_concurrent():
    scenarios = ['Write-Write\n(2 workers)', 'Write-Write\n(5 workers)', 'Write-Write\n(10 workers)',
                 'Read-Write\n(2 workers)', 'Read-Write\n(5 workers)', 'Read-Write\n(10 workers)',
                 'Directory\n(2 workers)', 'Directory\n(5 workers)', 'Directory\n(10 workers)']
    bare_corrupt = [67.80, 95.68, 98.64, 34.60, 31.93, 9.12, 0.00, 1.47, 2.73]
    guarded_corrupt = [0.00] * 9

    x = np.arange(len(scenarios))
    w = 0.35

    fig, ax = plt.subplots(figsize=(9, 4.5))
    bars1 = ax.bar(x - w/2, bare_corrupt, w, label='Bare (unprotected)', color='#EF4444', edgecolor='#DC2626', linewidth=0.5)
    bars2 = ax.bar(x + w/2, guarded_corrupt, w, label='Guarded (CADVP v1.1)', color='#16A34A', edgecolor='#15803D', linewidth=0.5)

    ax.set_ylabel('Corruption Rate (%)')
    ax.set_title('T5: Concurrent Conflict Detection (90 trials)')
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=8)
    ax.set_ylim(0, 110)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))
    ax.legend(loc='upper left', framealpha=0.9)

    for bar in bars1:
        h = bar.get_height()
        if h > 1:
            ax.text(bar.get_x() + bar.get_width()/2., h + 2, f'{h:.1f}%', ha='center', va='bottom', fontsize=8, fontweight='bold', color='#DC2626')
    for bar in bars2:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., h + 2, '0.0%', ha='center', va='bottom', fontsize=8, fontweight='bold', color='#16A34A')

    # Annotation line
    ax.annotate('Corruption eliminated\nat all concurrency levels', xy=(4, 40), xytext=(6, 65),
                fontsize=9, color='#16A34A', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#16A34A', lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#F0FDF4', edgecolor='#86EFAC'))
    fig.tight_layout()
    save(fig, 'concurrent_comparison.png')


# ─── T4: Exception Recovery Rollback ────────────────────────────────
def chart_rollback():
    scenarios = ['Clean Rollback', 'Idempotency', 'Checkpoint Recovery']
    bare_success = [0.0, None, 0.0]  # Idempotency doesn't apply to bare
    guarded_success = [100.0, 100.0, 100.0]
    bare_restore = [0.0, 100.0, 0.0]
    guarded_restore = [100.0, 100.0, 100.0]

    x = np.arange(len(scenarios))
    w = 0.3

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)

    # Left: Rollback Success
    b1 = ax1.bar(x - w/2, [s if s is not None else 0 for s in bare_success], w,
                 label='Bare', color='#FCA5A5', edgecolor='#DC2626', linewidth=0.5)
    b2 = ax1.bar(x + w/2, guarded_success, w,
                 label='Guarded', color='#86EFAC', edgecolor='#16A34A', linewidth=0.5)
    ax1.set_title('Rollback Success Rate')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios, fontsize=9)
    ax1.set_ylabel('Success Rate (%)')
    ax1.set_ylim(0, 120)
    ax1.legend(loc='lower right')
    for bar, val in zip(b1, [0, 0, 0]):
        if val is not None:
            ax1.text(bar.get_x() + bar.get_width()/2., val + 2, f'{val:.0f}%', ha='center', fontsize=8, fontweight='bold', color='#DC2626')
    for bar, val in zip(b2, guarded_success):
        ax1.text(bar.get_x() + bar.get_width()/2., val + 2, f'{val:.0f}%', ha='center', fontsize=8, fontweight='bold', color='#16A34A')

    # Right: State Restoration
    b3 = ax2.bar(x - w/2, bare_restore, w,
                 label='Bare', color='#FCA5A5', edgecolor='#DC2626', linewidth=0.5)
    b4 = ax2.bar(x + w/2, guarded_restore, w,
                 label='Guarded', color='#86EFAC', edgecolor='#16A34A', linewidth=0.5)
    ax2.set_title('State Restoration Rate')
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenarios, fontsize=9)
    ax2.legend(loc='lower right')
    for bar, val in zip(b3, bare_restore):
        ax2.text(bar.get_x() + bar.get_width()/2., val + 2, f'{val:.0f}%' if val > 0 else '0%', ha='center', fontsize=8, fontweight='bold', color='#DC2626' if val == 0 else '#16A34A')
    for bar, val in zip(b4, guarded_restore):
        ax2.text(bar.get_x() + bar.get_width()/2., val + 2, f'{val:.0f}%', ha='center', fontsize=8, fontweight='bold', color='#16A34A')

    fig.suptitle('T4: Exception Recovery Rollback (60 trials)', fontsize=13, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save(fig, 'rollback_comparison.png')


# ─── T3: Cross-Agent Relay ──────────────────────────────────────────
def chart_relay():
    scenarios = ['Tech → Marketing', 'Data Compression', 'Instruction Relay']
    bare_preserve = [93.0, 87.0, 94.0]
    guarded_preserve = [100.0, 100.0, 100.0]
    bare_distort = [0.7, 1.3, 0.9]
    guarded_distort = [0.0, 0.0, 0.0]

    x = np.arange(len(scenarios))
    w = 0.35

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))

    # Left: Information Preservation
    b1 = ax1.bar(x - w/2, bare_preserve, w, label='Bare', color='#FCA5A5', edgecolor='#DC2626', linewidth=0.5)
    b2 = ax1.bar(x + w/2, guarded_preserve, w, label='Guarded', color='#86EFAC', edgecolor='#16A34A', linewidth=0.5)
    ax1.set_title('Information Preservation')
    ax1.set_ylabel('Preservation Rate (%)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios, fontsize=9)
    ax1.set_ylim(75, 105)
    ax1.legend(loc='lower right')
    for bar, val in zip(b1, bare_preserve):
        ax1.text(bar.get_x() + bar.get_width()/2., val + 0.5, f'{val:.0f}%', ha='center', fontsize=8, fontweight='bold', color='#DC2626')
    for bar, val in zip(b2, guarded_preserve):
        ax1.text(bar.get_x() + bar.get_width()/2., val + 0.5, f'{val:.0f}%', ha='center', fontsize=8, fontweight='bold', color='#16A34A')

    # Right: Distortions
    b3 = ax2.bar(x - w/2, bare_distort, w, label='Bare', color='#FCA5A5', edgecolor='#DC2626', linewidth=0.5)
    b4 = ax2.bar(x + w/2, guarded_distort, w, label='Guarded', color='#86EFAC', edgecolor='#16A34A', linewidth=0.5)
    ax2.set_title('Average Distortions per Relay')
    ax2.set_ylabel('Distortion Count')
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenarios, fontsize=9)
    ax2.set_ylim(0, 2.0)
    ax2.legend(loc='upper right')
    for bar, val in zip(b3, bare_distort):
        ax2.text(bar.get_x() + bar.get_width()/2., val + 0.05, f'{val:.1f}', ha='center', fontsize=8, fontweight='bold', color='#DC2626')
    for bar, val in zip(b4, guarded_distort):
        ax2.text(bar.get_x() + bar.get_width()/2., val + 0.05, '0.0', ha='center', fontsize=8, fontweight='bold', color='#16A34A')

    fig.suptitle('T3: Cross-Agent Relay (60 trials)', fontsize=13, fontweight='bold')
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    save(fig, 'relay_comparison.png')


# ─── All Experiments Summary ────────────────────────────────────────
def chart_summary():
    metrics = ['Concurrent\nCorruption\n(10 workers)', 'Relay Info\nPreservation', 'Rollback\nSuccess', 'Checkpoint\nRecovery']
    bare_vals = [98.64, 91.3, 0.0, 0.0]
    guarded_vals = [0.0, 100.0, 100.0, 100.0]
    # Average bare for relay: (93+87+94)/3
    bare_label = ['98.6%', '91.3%', '0%', '0%']
    guarded_label = ['0.0%', '100%', '100%', '100%']

    x = np.arange(len(metrics))
    w = 0.35

    fig, ax = plt.subplots(figsize=(9, 4.5))
    b1 = ax.bar(x - w/2, bare_vals, w, label='Bare (unprotected)', color='#EF4444', edgecolor='#DC2626', linewidth=0.5)
    b2 = ax.bar(x + w/2, guarded_vals, w, label='Guarded (CADVP v1.1)', color='#16A34A', edgecolor='#15803D', linewidth=0.5)

    ax.set_ylabel('Rate (%)')
    ax.set_title('Aggregate Experiment Results (210 total trials)', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=9)
    ax.set_ylim(0, 120)
    ax.legend(loc='upper right', framealpha=0.9)

    for bar, val, lbl in zip(b1, bare_vals, bare_label):
        if val > 1:
            ax.text(bar.get_x() + bar.get_width()/2., val + 2, lbl, ha='center', va='bottom', fontsize=9, fontweight='bold', color='#DC2626')
        else:
            ax.text(bar.get_x() + bar.get_width()/2., 3, lbl, ha='center', va='bottom', fontsize=9, fontweight='bold', color='#DC2626')
    for bar, val, lbl in zip(b2, guarded_vals, guarded_label):
        ax.text(bar.get_x() + bar.get_width()/2., val + 2, lbl, ha='center', va='bottom', fontsize=9, fontweight='bold', color='#16A34A')

    # Big annotation
    ax.annotate('CADVP achieves 100%\nreliability across all tests', xy=(2.5, 55), xytext=(0.5, 75),
                fontsize=10, color='#16A34A', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color='#16A34A', lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#F0FDF4', edgecolor='#86EFAC'))

    fig.tight_layout()
    save(fig, 'all_experiments_summary.png')


if __name__ == '__main__':
    chart_concurrent()
    chart_rollback()
    chart_relay()
    chart_summary()
    print('\nAll 4 charts generated successfully.')
