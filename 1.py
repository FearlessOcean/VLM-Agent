import matplotlib.pyplot as plt
import numpy as np

# 1. 环境配置
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'serif'

# 绘制严谨直角符号的辅助函数
def plot_angle_mark(ax, pt, p1, p2, size=0.28):
    """
    根据给定的两条射线方向绘制平行四边形直角标记。
    pt: 顶点
    p1, p2: 定义射线方向的两个远端点（自动确定符号绘制在哪两个夹角内）
    """
    v1 = (p1 - pt) / np.linalg.norm(p1 - pt)
    v2 = (p2 - pt) / np.linalg.norm(p2 - pt)
    corner1 = pt + v1 * size
    corner_mid = pt + v1 * size + v2 * size
    corner2 = pt + v2 * size
    ax.plot([corner1[0], corner_mid[0], corner2[0]], 
            [corner1[1], corner_mid[1], corner2[1]], 'k-', lw=1.5)

# 直线求交点的解析几何函数
def get_intersection(p1, p2, p3, p4):
    x1, y1 = p1; x2, y2 = p2
    x3, y3 = p3; x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:
        return None
    num_x = (x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
    num_y = (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
    return np.array([num_x / den, num_y / den])

def draw_dynamic_geometry(theta_deg=55):
    fig, ax = plt.subplots(figsize=(7, 7))
    
    # 2. 定义固定结构: 等腰直角三角形 ABC
    A = np.array([-2.0, 0.0])
    B = np.array([2.0, 0.0])
    C = np.array([0.0, 2.0])  # C落在以AB为直径的圆上，完美等腰直角
    
    # 3. 自定义 D 的参数化位置 (落在以AB为直径的圆弧上以保证 ABD 是直角)
    theta_rad = np.radians(theta_deg)
    R = 2.0  
    D = np.array([R * np.cos(theta_rad), R * np.sin(theta_rad)])
    
    # 4. 自动推导计算出交点 M 和 E
    M = get_intersection(A, C, B, D)
    E = get_intersection(A, D, B, C)
    
    # --- 开始绘制图像 ---
    lw = 2.0
    
    # 绘制主要线段
    ax.plot([A[0], B[0]], [A[1], B[1]], 'k-', lw=lw) # 底边 AB
    ax.plot([A[0], M[0]],[A[1], M[1]], 'k-', lw=lw) # 直线 AM (必定通过C)
    ax.plot([B[0], M[0]], [B[1], M[1]], 'k-', lw=lw) # 直线 BM (必定通过D)
    
    # 绘制内部交叉连线
    ax.plot([B[0], C[0]], [B[1], C[1]], 'k-', lw=lw) # 线段 BC
    ax.plot([A[0], D[0]], [A[1], D[1]], 'k-', lw=lw) # 线段 AD
    ax.plot([C[0], D[0]], [C[1], D[1]], 'k-', lw=lw) # 线段 CD
    
    # 5. 【新增修复】严格按照您的指定添加并定向所有的直角符号
    # ① 标记 AMD 为直角：落在由 M 发出的射线 MA 与 MD（MB）之间
    plot_angle_mark(ax, M, A, D, size=0.28)
    
    # ② 内部标记 ACB：落在由 C 发出的射线 CA 与 CB 之间（朝三角形内部向下）
    plot_angle_mark(ax, C, A, B, size=0.28)
    
    # ③ 内部标记 ADB：落在由 D 发出的射线 DA 与 DB 之间（朝三角形内部向下）
    plot_angle_mark(ax, D, A, B, size=0.28)
    
    # 6. 标注字母及完美避让保护
    fs = 26
    ax.text(A[0]-0.25, A[1]-0.15, '$A$', ha='center', va='top', fontsize=fs)
    ax.text(B[0]+0.25, B[1]-0.15, '$B$', ha='center', va='top', fontsize=fs)
    ax.text(M[0], M[1]+0.15, '$M$', ha='center', va='bottom', fontsize=fs)
    # C点标签向外侧上（左）偏置避让直角符
    ax.text(C[0]-0.25, C[1]+0.1, '$C$', ha='right', va='bottom', fontsize=fs)
    # D点标签向外侧上（右）偏置避让直角符
    ax.text(D[0]+0.25, D[1]+0.1, '$D$', ha='left', va='bottom', fontsize=fs)
    ax.text(E[0], E[1]-0.25, '$E$', ha='center', va='top', fontsize=fs)
    
    # 7. 自适应边界，确保图像居中、不截断
    ax.set_aspect('equal')
    ax.axis('off')
    
    all_pts = np.array([A, B, C, D, M, E])
    min_x, max_x = np.min(all_pts[:, 0]), np.max(all_pts[:, 0])
    min_y, max_y = np.min(all_pts[:, 1]), np.max(all_pts[:, 1])
    
    ax.set_xlim(min_x - 0.8, max_x + 0.8)
    ax.set_ylim(min_y - 0.6, max_y + 0.6)
    
    # 8. 保存输出
    plt.savefig('question.png', dpi=300, bbox_inches='tight')
    plt.close(fig)

if __name__ == "__main__":
    # 参数 D 的生成角度保持 55 度，以获得接近参考图形重心的美观视图
    draw_dynamic_geometry(theta_deg=55)