/**
 * API 封装
 * 统一处理 HTTP 请求、响应和错误
 */

import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'

/**
 * 统一的分页响应类型
 * 后端返回格式：{ errorCode: 0, message: "success", data: [], page: { total, page, pageSize } }
 */
export interface PaginatedResponse<T> {
  data: T[]
  page: {
    total: number
    page: number
    pageSize: number
  }
  meta?: Record<string, any> // 额外的元数据（如搜索接口的 took、keyword 等）
}

// API 基础配置
// 优先级：环境变量 > Docker环境相对路径 > 本地开发相对路径（通过vite代理）
// 在 Docker 环境和本地开发时，都使用相对路径，通过 vite 代理转发到后端
const getApiBaseUrl = (): string => {
  // 如果设置了环境变量，优先使用
  const envApiUrl = import.meta.env.VITE_API_BASE_URL
  if (envApiUrl) {
    // 如果是完整 URL，会在后续步骤中自动转换为相对路径
    // 这里直接返回，让后续的统一处理逻辑来处理
    return envApiUrl
  }
  
  // Docker 环境或生产环境，使用相对路径（通过 vite 代理）
  if (import.meta.env.DOCKER_ENV === 'true' || import.meta.env.PROD) {
    return '/api/v1'
  }
  
  // 本地开发环境，使用相对路径（通过 vite 代理）
  return '/api/v1'
}

let API_BASE_URL = getApiBaseUrl()

// 强制确保使用相对路径（不以 http:// 或 https:// 开头）
if (API_BASE_URL.startsWith('http://') || API_BASE_URL.startsWith('https://')) {
  // 提取路径部分
  try {
    const url = new URL(API_BASE_URL)
    const correctedPath = url.pathname || '/api/v1'
    if (import.meta.env.DEV) {
      console.warn('提示: 检测到完整 URL，已自动转换为相对路径')
      console.warn('原始值:', API_BASE_URL)
      console.warn('修正后:', correctedPath)
    }
    API_BASE_URL = correctedPath
  } catch {
    if (import.meta.env.DEV) {
      console.warn('提示: 无法解析 URL，使用默认相对路径 /api/v1')
    }
    API_BASE_URL = '/api/v1'
  }
}

// 确保以 / 开头
if (!API_BASE_URL.startsWith('/')) {
  API_BASE_URL = '/' + API_BASE_URL
}

// 开发环境下输出配置信息，方便调试
if (import.meta.env.DEV) {
  console.log('=== API 配置信息 ===')
  console.log('VITE_API_BASE_URL (环境变量):', import.meta.env.VITE_API_BASE_URL)
  console.log('DOCKER_ENV:', import.meta.env.DOCKER_ENV)
  console.log('最终 API_BASE_URL:', API_BASE_URL)
  console.log('==================')
}

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加 token
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    // FormData 时由浏览器自动设置 Content-Type（含 boundary）
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    const { data } = response
    
    // 统一响应格式处理
    if (data.errorCode === 0 || data.errorCode === 200) {
      // 如果是分页响应（包含 page 字段），返回完整的分页结构
      if (data.page && Array.isArray(data.data)) {
        return {
          data: data.data,
          page: data.page,
          meta: data.meta || {}
        }
      }
      // 普通响应，返回 data 字段或整个 data
      return data.data !== undefined ? data.data : data
    } else {
      ElMessage.error(data.message || '请求失败')
      return Promise.reject(new Error(data.message || '请求失败'))
    }
  },
  (error) => {
    // 错误处理
    if (error.response) {
      const { status, data, config } = error.response
      
      // 登录接口的 401 错误由登录页面自己处理，不在这里统一处理
      const isLoginRequest = config?.url?.includes('/auth/login')
      
      // 开发环境下输出错误信息，方便调试
      if (import.meta.env.DEV && isLoginRequest) {
        console.log('登录错误响应:', {
          status,
          data,
          fullError: error.response
        })
      }
      
      switch (status) {
        case 401:
          if (isLoginRequest) {
            // 登录接口的错误，直接 reject，让登录页面处理
            // 不显示消息，不跳转，让登录页面显示具体的错误信息
            // 确保 error.response.data 被正确传递
          } else {
            // 其他接口的 401 错误，清除 token 并跳转到登录页
            ElMessage.error('未授权，请重新登录')
            localStorage.removeItem('token')
            sessionStorage.removeItem('token')
            window.location.href = '/login'
          }
          break
        case 403:
          ElMessage.error('没有权限访问')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error('服务器错误')
          break
        default:
          ElMessage.error(data?.message || `请求失败: ${status}`)
      }
    } else if (error.request) {
      // 只有非登录请求才显示网络错误消息
      const isLoginRequest = error.config?.url?.includes('/auth/login')
      if (!isLoginRequest) {
        ElMessage.error('网络错误，请检查网络连接')
      }
    } else {
      // 只有非登录请求才显示配置错误消息
      const isLoginRequest = error.config?.url?.includes('/auth/login')
      if (!isLoginRequest) {
        ElMessage.error('请求配置错误')
      }
    }
    
    // 确保完整的 error 对象被传递，包括 response.data
    // 对于登录请求，确保 response.data 被正确传递
    if (error.response && error.config?.url?.includes('/auth/login')) {
      // 开发环境下验证错误对象结构
      if (import.meta.env.DEV) {
        console.log('响应拦截器 reject 的错误对象:', {
          hasResponse: !!error.response,
          hasData: !!error.response?.data,
          data: error.response?.data,
          message: error.response?.data?.message
        })
      }
    }
    
    return Promise.reject(error)
  }
)

// 通用请求方法
export const request = {
  get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return apiClient.get(url, config)
  },
  
  post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return apiClient.post(url, data, config)
  },
  
  put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    return apiClient.put(url, data, config)
  },
  
  delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
    return apiClient.delete(url, config)
  },
  
  upload<T = any>(url: string, formData: FormData, config?: AxiosRequestConfig): Promise<T> {
    return apiClient.post(url, formData, {
      ...config,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config?.headers
      }
    })
  }
}

export default apiClient
