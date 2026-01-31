/**
 * 认证相关 API
 */
import request from './index'

export interface LoginRequest {
  username: string
  password: string
  encrypted?: boolean
}

export interface PublicKeyResponse {
  publicKey: string
  publicKeyBase64: string
}

export interface LoginResponse {
  token: string
  user: {
    id: number
    username: string
    realName: string
    role: string
  }
}

export const authApi = {
  // 获取 RSA 公钥
  async getPublicKey(): Promise<PublicKeyResponse> {
    const response = await request.get<{ data: PublicKeyResponse }>('/auth/public-key')
    // 如果返回的是包装格式，提取 data 字段
    return (response as any).data || response
  },
  
  // 登录
  login(data: LoginRequest): Promise<LoginResponse> {
    return request.post('/auth/login', data)
  },
  
  // 登出
  logout(): Promise<void> {
    return request.post('/auth/logout')
  },
  
  // 刷新 token
  refreshToken(): Promise<{ token: string }> {
    return request.post('/auth/refresh')
  }
}
