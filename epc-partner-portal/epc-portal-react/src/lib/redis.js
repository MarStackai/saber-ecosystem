import { Redis } from '@upstash/redis'

// For development, we'll use a simple in-memory storage fallback
// In production, you would set REDIS_URL
let redis = null

if (process.env.REDIS_URL) {
  // Use Redis URL directly with Upstash client
  redis = new Redis({
    url: process.env.REDIS_URL
  })
  
  console.log('✅ Connected to Redis Cloud via Upstash')
} else {
  // Development fallback - simple in-memory store
  const memoryStore = new Map()
  
  redis = {
    async set(key, value, options = {}) {
      const serialized = JSON.stringify(value)
      memoryStore.set(key, serialized)
      
      // Handle TTL (time to live)
      if (options.ex) {
        setTimeout(() => {
          memoryStore.delete(key)
        }, options.ex * 1000)
      }
      
      return 'OK'
    },
    
    async get(key) {
      const value = memoryStore.get(key)
      return value ? JSON.parse(value) : null
    },
    
    async del(key) {
      return memoryStore.delete(key) ? 1 : 0
    },
    
    async exists(key) {
      return memoryStore.has(key) ? 1 : 0
    },
    
    async expire(key, seconds) {
      if (memoryStore.has(key)) {
        setTimeout(() => {
          memoryStore.delete(key)
        }, seconds * 1000)
        return 1
      }
      return 0
    }
  }
  
  console.log('⚠️  Using in-memory Redis fallback for development')
}

export { redis }

// Helper functions for EPC application data
export const epcRedisHelpers = {
  // Generate key for EPC application
  getKey(invitationCode, suffix = '') {
    const timestamp = Date.now()
    return suffix 
      ? `epc:${invitationCode}:${suffix}:${timestamp}`
      : `epc:${invitationCode}:${timestamp}`
  },
  
  // Store complete application data
  async storeApplication(invitationCode, formData, files = {}) {
    const key = this.getKey(invitationCode, 'application')
    const data = {
      invitationCode,
      formData,
      files: Object.keys(files).reduce((acc, fieldName) => {
        if (files[fieldName]) {
          acc[fieldName] = {
            name: files[fieldName].name,
            size: files[fieldName].size,
            type: files[fieldName].type,
            uploadedAt: files[fieldName].uploadedAt
          }
        }
        return acc
      }, {}),
      status: 'pending',
      submissionTimestamp: new Date().toISOString(),
      sharePointId: null
    }
    
    // Store for 24 hours (86400 seconds)
    if (redis.setex) {
      // Upstash Redis client
      await redis.setex(key, 86400, JSON.stringify(data))
    } else {
      // In-memory fallback
      await redis.set(key, data, { ex: 86400 })
    }
    return key
  },
  
  // Retrieve application data
  async getApplication(key) {
    const result = await redis.get(key)
    if (redis.setex && result) {
      // Upstash Redis client returns string, parse JSON
      return JSON.parse(result)
    }
    return result
  },
  
  // Update application status
  async updateStatus(key, status, sharePointId = null) {
    const data = await this.getApplication(key)
    if (data) {
      data.status = status
      if (sharePointId) {
        data.sharePointId = sharePointId
      }
      data.lastUpdated = new Date().toISOString()
      
      if (redis.setex) {
        // Upstash Redis client
        await redis.setex(key, 86400, JSON.stringify(data))
      } else {
        // In-memory fallback
        await redis.set(key, data, { ex: 86400 })
      }
    }
    return data
  },
  
  // Clean up processed applications
  async cleanup(key) {
    return await redis.del(key)
  },

  // Store draft form data for auto-save
  async saveDraft(invitationCode, formData, currentStep) {
    const key = `epc:draft:${invitationCode}`
    const draftData = {
      formData,
      currentStep,
      lastSaved: new Date().toISOString(),
      status: 'draft'
    }
    
    // Store draft for 7 days (604800 seconds)
    if (redis.setex) {
      await redis.setex(key, 604800, JSON.stringify(draftData))
    } else {
      await redis.set(key, draftData, { ex: 604800 })
    }
    return key
  },

  // Retrieve draft form data
  async getDraft(invitationCode) {
    const key = `epc:draft:${invitationCode}`
    const result = await redis.get(key)
    if (redis.setex && result) {
      return JSON.parse(result)
    }
    return result
  },

  // Remove draft after successful submission
  async clearDraft(invitationCode) {
    const key = `epc:draft:${invitationCode}`
    return await redis.del(key)
  }
}