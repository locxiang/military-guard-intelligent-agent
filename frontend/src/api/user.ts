/**
 * 用户管理相关 API
 */
import request, { type PaginatedResponse } from './index'

export interface User {
  id: number
  username: string
  realName?: string
  department?: string
  role: 'admin' | 'user'
  status: 0 | 1
  createdAt: Date | string
  updatedAt: Date | string
}

export interface UserListParams {
  keyword?: string
  role?: 'admin' | 'user'
  status?: 0 | 1
  page?: number
  pageSize?: number
}

export interface UserCreateRequest {
  username: string
  password: string
  realName?: string
  department?: string
  role?: 'admin' | 'user'
  encrypted?: boolean
}

export interface UserUpdateRequest {
  realName?: string
  department?: string
  role?: 'admin' | 'user'
  status?: 0 | 1
}

export const userApi = {
  // 获取用户列表
  getList(params: UserListParams): Promise<PaginatedResponse<User>> {
    return request.get('/user/list', { params })
  },
  
  // 获取用户详情
  getDetail(id: number): Promise<User> {
    return request.get(`/user/${id}`)
  },
  
  // 创建用户
  create(data: UserCreateRequest): Promise<User> {
    return request.post('/user', data)
  },
  
  // 更新用户
  update(id: number, data: UserUpdateRequest): Promise<User> {
    return request.put(`/user/${id}`, data)
  },
  
  // 删除用户
  delete(id: number): Promise<void> {
    return request.delete(`/user/${id}`)
  },
  
  // 启用/禁用用户
  updateStatus(id: number, status: 0 | 1): Promise<void> {
    return request.put(`/user/${id}/status`, { status })
  },
  
  // 重置密码
  resetPassword(id: number, password: string, encrypted?: boolean): Promise<void> {
    return request.put(`/user/${id}/password`, { password, encrypted })
  }
}
