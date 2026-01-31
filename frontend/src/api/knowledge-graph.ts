/**
 * 知识图谱相关 API
 */
import request from './index'

export interface KnowledgeGraphQuery {
  entity_type: string
  entity_id?: string
  relation_type?: string
  hop_count?: number
}

export interface KnowledgeGraphResponse {
  entity: {
    id: string
    name: string
    type: string
  }
  relations: Array<{
    targetEntity: {
      id: string
      name: string
      type: string
    }
    relation: string
    desc: string
  }>
}

export const knowledgeGraphApi = {
  // 查询知识图谱
  query(params: KnowledgeGraphQuery): Promise<KnowledgeGraphResponse> {
    return request.get('/knowledge-graph/query', { params })
  },
  
  // 创建实体
  createEntity(entityType: string, entityName: string, properties?: Record<string, any>): Promise<any> {
    return request.post('/knowledge-graph/entity', null, {
      params: {
        entity_type: entityType,
        entity_name: entityName,
        properties
      }
    })
  },
  
  // 获取关联关系
  getRelations(entityType?: string): Promise<{ relations: any[] }> {
    return request.get('/knowledge-graph/relations', { params: { entity_type: entityType } })
  }
}
