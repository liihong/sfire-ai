/**
 * 公共工具函数
 */

/**
 * 验证并获取有效的模型类型
 */
export function getValidModelType(modelType: string | undefined | null, defaultType: string = 'doubao'): string {
  const validTypes = ['deepseek', 'doubao', 'claude']
  if (!modelType || typeof modelType !== 'string' || !validTypes.includes(modelType)) {
    return defaultType
  }
  return modelType
}

/**
 * 返回上一页的通用函数
 */
export function goBack() {
  uni.navigateBack({
    fail: () => {
      uni.switchTab({ url: '/pages/index/index' })
    }
  })
}

