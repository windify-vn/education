import axios from 'axios'

// Create axios instance with default config
const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
})

export function useApi() {
  const handleResponse = (response) => {
    return response.data
  }

  const handleError = (error) => {
    // Extract error message from axios error
    const errorData = error.response?.data || error.message || error
    throw errorData
  }

  const get = async (url, params = {}) => {
    try {
      const response = await api.get(url, { params })
      return handleResponse(response)
    } catch (error) {
      throw handleError(error)
    }
  }

  const post = async (url, data = {}) => {
    try {
      const response = await api.post(url, data)
      return handleResponse(response)
    } catch (error) {
      throw handleError(error)
    }
  }

  const put = async (url, data = {}) => {
    try {
      const response = await api.put(url, data)
      return handleResponse(response)
    } catch (error) {
      throw handleError(error)
    }
  }

  const del = async (url) => {
    try {
      const response = await api.delete(url)
      return handleResponse(response)
    } catch (error) {
      throw handleError(error)
    }
  }

  const uploadFile = async (file, options = {}) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_name', file.name)
    formData.append('filename', file.name)
    formData.append('is_private', options.isPrivate ? '1' : '0')
    
    if (options.folder) formData.append('folder', options.folder)
    if (options.doctype) formData.append('doctype', options.doctype)
    if (options.docname) formData.append('docname', options.docname)
    if (options.fieldname) formData.append('fieldname', options.fieldname)

    try {
      const response = await api.post('/method/upload_file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return handleResponse(response)
    } catch (error) {
      throw handleError(error)
    }
  }

  // Upload file dành cho Education app (public, folder mặc định Home/Homework)
  const uploadEducationFile = async (file, options = {}) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('file_name', file.name)
    formData.append('filename', file.name)

    if (options.folder) formData.append('folder', options.folder)
    if (options.doctype) formData.append('doctype', options.doctype)
    if (options.docname) formData.append('docname', options.docname)
    if (options.fieldname) formData.append('fieldname', options.fieldname)

    try {
      const response = await api.post('/method/education.education.api.upload_education_file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return handleResponse(response)
    } catch (error) {
      throw handleError(error)
    }
  }

  return {
    get,
    post,
    put,
    delete: del,
    uploadFile,
    uploadEducationFile
  }
}
