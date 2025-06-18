import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.stats.proportion as proportion  # 添加statsmodels库

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取所有CSV文件
ab_test = pd.read_csv("AB实验分析.csv")
ads_exposure = pd.read_csv("广告曝光量分析.csv")
day_effect = pd.read_csv("星期几的转化效果.csv")
hour_effect = pd.read_csv("小时段的转化效果.csv")


# 1. AB实验组与对照组转化率差异检验
def ab_test_proportion_test(df):
    ad_group = df[df['test_group'] == 'ad']
    psa_group = df[df['test_group'] == 'psa']

    # 提取数据
    n1 = ad_group['total_users'].values[0]
    conv1 = ad_group['converted_users'].values[0]
    n2 = psa_group['total_users'].values[0]
    conv2 = psa_group['converted_users'].values[0]

    # 计算转化率
    p1 = conv1 / n1
    p2 = conv2 / n2

    # 使用statsmodels进行比例检验
    z_stat, p_value = proportion.proportions_ztest([conv1, conv2], [n1, n2])

    # 计算置信区间
    pooled_p = (conv1 + conv2) / (n1 + n2)
    se = np.sqrt(pooled_p * (1 - pooled_p) * (1 / n1 + 1 / n2))
    ci_low = (p1 - p2) - 1.96 * se
    ci_high = (p1 - p2) + 1.96 * se

    print("=" * 60)
    print("AB测试转化率差异检验:")
    print(f"- 广告组转化率: {p1 * 100:.2f}% ({conv1}/{n1})")
    print(f"- 对照组转化率: {p2 * 100:.2f}% ({conv2}/{n2})")
    print(f"- 比例差异: {(p1 - p2) * 100:.2f}% [95%CI: {ci_low * 100:.2f}%, {ci_high * 100:.2f}%]")
    print(f"- Z统计量: {z_stat:.4f}, P值: {p_value:.10f}")

    # 结果解释
    alpha = 0.05
    if p_value < alpha:
        print(f"结论: 广告组与对照组转化率存在显著差异 (p < {alpha})")
    else:
        print(f"结论: 广告组与对照组转化率无显著差异 (p > {alpha})")

    # 可视化
    plt.figure(figsize=(10, 6))
    sns.barplot(x='test_group', y='conversion_rate', data=df, palette=['#1f77b4', '#ff7f0e'])
    plt.title('AB测试转化率比较')
    plt.ylabel('转化率 (%)')
    plt.xlabel('实验分组')
    plt.ylim(0, df['conversion_rate'].max() * 1.2)

    # 添加数值标签
    for i, row in df.iterrows():
        plt.text(i, row['conversion_rate'] + 0.05,
                 f"{row['conversion_rate']}%",
                 ha='center', fontsize=12)

    plt.tight_layout()
    plt.savefig('ab_test_comparison.png', dpi=300)
    plt.show()


# 2. 广告曝光量分桶转化率差异检验
def ads_exposure_chi2_test(df):
    # 准备列联表数据
    observed = df[['conversions', 'users']].copy()
    observed['non_conversions'] = observed['users'] - observed['conversions']
    contingency_table = observed[['conversions', 'non_conversions']].values

    # 执行卡方检验
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

    print("\n" + "=" * 60)
    print("广告曝光量分桶转化率差异检验:")
    print(f"- 卡方统计量: {chi2:.2f}, 自由度: {dof}, P值: {p_value:.10f}")

    # 结果解释
    alpha = 0.05
    if p_value < alpha:
        print(f"结论: 不同广告曝光量分桶的转化率存在显著差异 (p < {alpha})")
    else:
        print(f"结论: 不同广告曝光量分桶的转化率无显著差异 (p > {alpha})")

    # 计算效应量 (Cramer's V)
    n = observed['users'].sum()
    cramers_v = np.sqrt(chi2 / (n * min(contingency_table.shape[0] - 1, contingency_table.shape[1] - 1)))
    print(f"- 效应量 (Cramer's V): {cramers_v:.3f}")

    # 可视化
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(x='ads_bucket', y='conversion_rate', data=df, palette='viridis')
    plt.title('不同广告曝光量分桶的转化率')
    plt.ylabel('转化率 (%)')
    plt.xlabel('广告曝光量分桶')
    plt.ylim(0, df['conversion_rate'].max() * 1.2)

    # 添加数值标签
    for i, row in df.iterrows():
        ax.text(i, row['conversion_rate'] + 0.3,
                f"{row['conversion_rate']}%",
                ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig('ads_exposure_comparison.png', dpi=300)
    plt.show()

    # 返回效应量
    return cramers_v


# 3. 星期几转化率差异检验
def day_effect_chi2_test(df):
    # 计算转化用户数 (四舍五入取整)
    df['conversions'] = round(df['impressions'] * df['conversion_rate'] / 100).astype(int)
    df['non_conversions'] = df['impressions'] - df['conversions']

    # 准备列联表数据
    contingency_table = df[['conversions', 'non_conversions']].values

    # 执行卡方检验
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

    print("\n" + "=" * 60)
    print("星期几转化率差异检验:")
    print(f"- 卡方统计量: {chi2:.2f}, 自由度: {dof}, P值: {p_value:.10f}")

    # 结果解释
    alpha = 0.05
    if p_value < alpha:
        print(f"结论: 一周中不同日期的转化率存在显著差异 (p < {alpha})")
    else:
        print(f"结论: 一周中不同日期的转化率无显著差异 (p > {alpha})")

    # 可视化
    plt.figure(figsize=(12, 8))
    ax = sns.barplot(x='most_ads_day', y='conversion_rate', data=df,
                     order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                     palette='coolwarm')
    plt.title('一周中各天的转化率比较')
    plt.ylabel('转化率 (%)')
    plt.xlabel('星期几')
    plt.ylim(0, df['conversion_rate'].max() * 1.2)

    # 添加数值标签
    for i, row in df.iterrows():
        ax.text(i, row['conversion_rate'] + 0.05,
                f"{row['conversion_rate']}%",
                ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig('day_effect_comparison.png', dpi=300)
    plt.show()

    # 返回处理后的数据
    return df


# 4. 小时段转化率趋势分析与检验
def hour_effect_analysis(df):
    # 计算转化用户数
    df['conversions'] = round(df['impressions'] * df['conversion_rate'] / 100).astype(int)

    # 执行卡方检验
    contingency_table = df[['conversions', 'impressions']].copy()
    contingency_table['non_conversions'] = contingency_table['impressions'] - contingency_table['conversions']
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table[['conversions', 'non_conversions']].values)

    print("\n" + "=" * 60)
    print("小时段转化率差异检验:")
    print(f"- 卡方统计量: {chi2:.2f}, 自由度: {dof}, P值: {p_value:.10f}")

    # 结果解释
    alpha = 0.05
    if p_value < alpha:
        print(f"结论: 一天中不同时间段的转化率存在显著差异 (p < {alpha})")
    else:
        print(f"结论: 一天中不同时间段的转化率无显著差异 (p > {alpha})")

    # 可视化
    plt.figure(figsize=(16, 8))

    # 创建双轴图
    ax1 = plt.gca()
    ax2 = ax1.twinx()

    # 转化率折线图
    sns.lineplot(x='most_ads_hour', y='conversion_rate', data=df,
                 marker='o', color='#d62728', ax=ax1, label='转化率')
    ax1.set_ylabel('转化率 (%)', color='#d62728')
    ax1.tick_params(axis='y', labelcolor='#d62728')
    ax1.set_ylim(0, df['conversion_rate'].max() * 1.2)

    # 曝光量柱状图
    sns.barplot(x='most_ads_hour', y='impressions', data=df,
                color='#1f77b4', alpha=0.6, ax=ax2, label='曝光量')
    ax2.set_ylabel('曝光量', color='#1f77b4')
    ax2.tick_params(axis='y', labelcolor='#1f77b4')

    # 设置标题和标签
    plt.title('不同小时段转化率与曝光量关系')
    plt.xlabel('小时')

    # 合并图例
    lines, labels = ax1.get_legend_handles_labels()
    bars, bar_labels = ax2.get_legend_handles_labels()
    ax2.legend(lines + bars, labels + bar_labels, loc='upper left')

    # 添加网格线
    ax1.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig('hour_effect_analysis.png', dpi=300)
    plt.show()

    # 返回处理后的数据
    return df


# 5. 广告曝光量与转化率的相关性分析
def exposure_conversion_correlation(ads_df):
    # 合并数据（这里使用广告曝光量分桶数据）
    plt.figure(figsize=(10, 6))

    # 计算每个分桶的中值曝光量（近似）
    ads_df['mid_exposure'] = ads_df['ads_bucket'].map({
        '0-50': 25,
        '51-100': 75,
        '101-200': 150,
        '200+': 250
    })

    # 计算相关系数
    r, p_val = stats.pearsonr(ads_df['mid_exposure'], ads_df['conversion_rate'])

    # 绘制散点图
    sns.regplot(x='mid_exposure', y='conversion_rate', data=ads_df,
                scatter_kws={'s': 100, 'alpha': 0.7},
                line_kws={'color': 'red'})

    plt.title('广告曝光量与转化率的相关性')
    plt.xlabel('广告曝光量（中值估计）')
    plt.ylabel('转化率 (%)')
    plt.grid(True, linestyle='--', alpha=0.7)

    # 添加相关系数注释
    plt.annotate(f'Pearson r = {r:.3f}\np = {p_val:.4f}',
                 xy=(0.7, 0.9), xycoords='axes fraction',
                 fontsize=12, bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

    plt.tight_layout()
    plt.savefig('exposure_conversion_correlation.png', dpi=300)
    plt.show()

    print("\n" + "=" * 60)
    print("广告曝光量与转化率的相关性分析:")
    print(f"- Pearson相关系数: {r:.3f}, P值: {p_val:.6f}")

    # 结果解释
    alpha = 0.05
    if p_val < alpha:
        if r > 0:
            print("结论: 广告曝光量与转化率存在显著正相关关系")
        else:
            print("结论: 广告曝光量与转化率存在显著负相关关系")
    else:
        print("结论: 广告曝光量与转化率无显著相关关系")


# 执行所有检验
ab_test_proportion_test(ab_test)
ads_exposure_chi2_test(ads_exposure)
day_effect = day_effect_chi2_test(day_effect)
hour_effect = hour_effect_analysis(hour_effect)

# 执行相关性分析
exposure_conversion_correlation(ads_exposure)