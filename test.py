import openai
import matplotlib
import numpy
import sys

print(f"Python Version: {sys.version}")
print(f"OpenAI Version: {openai.__version__}")
print(f"Matplotlib Version: {matplotlib.__version__}")
print(f"Numpy Version: {numpy.__version__}")

# 检查是否能正常打开绘图引擎
try:
    import matplotlib.pyplot as plt
    plt.figure()
    plt.close()
    print("✅ 绘图引擎正常")
except Exception as e:
    print(f"❌ 绘图引擎异常: {e}")