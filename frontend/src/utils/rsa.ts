/**
 * RSA 加密工具
 * 用于前端密码加密传输
 */
import JSEncrypt from 'jsencrypt'

/**
 * 使用 RSA 公钥加密密码
 * @param password 明文密码
 * @param publicKey PEM 格式的公钥
 * @returns Base64 编码的加密密码
 */
export function encryptPassword(password: string, publicKey: string): string {
  const encrypt = new JSEncrypt()
  encrypt.setPublicKey(publicKey)
  
  const encrypted = encrypt.encrypt(password)
  if (!encrypted) {
    throw new Error('密码加密失败，请检查公钥是否正确')
  }
  
  return encrypted
}

/**
 * 验证公钥格式
 * @param publicKey 公钥字符串
 * @returns 是否为有效的 PEM 格式公钥
 */
export function validatePublicKey(publicKey: string): boolean {
  return publicKey.includes('-----BEGIN PUBLIC KEY-----') && 
         publicKey.includes('-----END PUBLIC KEY-----')
}
