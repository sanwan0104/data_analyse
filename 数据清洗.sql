-- 计算各组转化率
SELECT
  test_group,
  COUNT(*) AS total_users,
  SUM(CASE WHEN converted = 'True' THEN 1 ELSE 0 END) AS converted_users,
  ROUND(SUM(CASE WHEN converted = 'True' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS conversion_rate
FROM marketing_ab
GROUP BY test_group;

-- 广告曝光量与转化率的关系
WITH bins AS (
  SELECT
    user_id,
    converted,
    total_ads,
    CASE
      WHEN total_ads <= 50 THEN '0-50'
      WHEN total_ads <= 100 THEN '51-100'
      WHEN total_ads <= 200 THEN '101-200'
      ELSE '200+'
    END AS ads_bucket
  FROM marketing_ab
  WHERE test_group = 'ad' -- 仅分析实验组
)
SELECT
  ads_bucket,
  COUNT(*) AS users,
  SUM(CASE WHEN converted = 'True' THEN 1 ELSE 0 END) AS conversions,
  ROUND(SUM(CASE WHEN converted = 'True' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS conversion_rate
FROM bins
GROUP BY ads_bucket
ORDER BY
  CASE ads_bucket
    WHEN '0-50' THEN 1
    WHEN '51-100' THEN 2
    WHEN '101-200' THEN 3
    ELSE 4
  END;
-- 星期几的转化效果
SELECT
  most_ads_day,
  COUNT(*) AS impressions,
  ROUND(AVG(CASE WHEN converted = 'True' THEN 1 ELSE 0 END) * 100, 2) AS conversion_rate
FROM marketing_ab
WHERE test_group = 'ad'
GROUP BY most_ads_day
ORDER BY
  CASE most_ads_day
    WHEN 'Monday' THEN 1
    WHEN 'Tuesday' THEN 2
    WHEN 'Wednesday' THEN 3
    WHEN 'Thursday' THEN 4
    WHEN 'Friday' THEN 5
    WHEN 'Saturday' THEN 6
    WHEN 'Sunday' THEN 7
  END;

-- 小时段的转化效果
SELECT
  most_ads_hour,
  COUNT(*) AS impressions,
  ROUND(AVG(CASE WHEN converted = 'True' THEN 1 ELSE 0 END) * 100, 2) AS conversion_rate
FROM marketing_ab
WHERE test_group = 'ad'
GROUP BY most_ads_hour
ORDER BY most_ads_hour;
