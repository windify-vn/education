<script setup>
import { ref, reactive } from 'vue'
import { FormControl, Textarea, Button, Dropdown } from 'frappe-ui'
import { useApi } from '@/composables/useApi'

const state = reactive({
  doctype: 'Homework',
  name: '',
  listParams: '',
  createData: '',
  updateData: '',
  // upload state
  fileObj: null,
  isPrivate: true,
  folder: 'Home/Homework',
  attachDoctype: '',
  attachDocname: '',
  attachFieldname: '',
})

const output = ref('')
const loading = ref(false)
const lastRaw = ref(null)
const { get, post, put, delete: del, uploadFile } = useApi()

function unwrapApi(value) {
  if (value && typeof value === 'object') {
    if (Object.prototype.hasOwnProperty.call(value, 'message') && value.message != null) {
      return value.message
    }
    if (Object.prototype.hasOwnProperty.call(value, 'data') && value.data != null) {
      return value.data
    }
  }
  return value
}

function setOutput(data, isSuccess = true) {
  const payload = unwrapApi(data)
  const status = isSuccess ? 'SUCCESS' : 'ERROR'

  const result = {
    status: status,
    timestamp: new Date().toISOString(),
    response: data,
  }

  lastRaw.value = result
  try {
    output.value = JSON.stringify(result, null, 2)
  } catch (_) {
    output.value = String(result)
  }
}

function getJson(s, fallback = {}) {
  try { return s ? JSON.parse(s) : fallback } catch { return fallback }
}

function parseJsonField(fieldKey, label) {
  const raw = state[fieldKey]
  if (!raw) return { ok: true, value: {} }
  try {
    const parsed = JSON.parse(raw)
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      return { ok: true, value: parsed }
    }
    return { ok: false, error: `${label} must be a JSON object` }
  } catch (e) {
    return { ok: false, error: `${label} has invalid JSON: ${e?.message || 'Parse error'}` }
  }
}

function formatField(fieldKey) {
  try {
    const parsed = getJson(state[fieldKey], {})
    state[fieldKey] = JSON.stringify(parsed, null, 2)
  } catch (_) {
    // keep as is on error
  }
}

function formatResult() {
  if (lastRaw.value != null) setOutput(lastRaw.value)
}

async function listDocs() {
  if (!state.doctype) return setOutput({ error: 'doctype is required' }, false)
  const params = getJson(state.listParams, {})

  try {
    const data = await get(`/resource/${encodeURIComponent(state.doctype)}`, params)
    setOutput(data, true)
    return data
  } catch (error) {
    setOutput(error, false)
    return error
  }
}

async function createDoc() {
  if (!state.doctype) return setOutput({ error: 'doctype is required' }, false)
  const parsed = parseJsonField('createData', 'Create Data')
  if (!parsed.ok) return setOutput({ error: parsed.error }, false)
  const data = parsed.value
  if (!data || Object.keys(data).length === 0) return setOutput({ error: 'Create Data must be a non-empty JSON object' }, false)

  try {
    const result = await post(`/resource/${encodeURIComponent(state.doctype)}`, data)
    setOutput(result, true)
    return result
  } catch (error) {
    setOutput(error, false)
    return error
  }
}

async function readDoc() {
  if (!state.doctype || !state.name) return setOutput({ error: 'doctype and name are required' }, false)

  try {
    const data = await get(`/resource/${encodeURIComponent(state.doctype)}/${encodeURIComponent(state.name)}`)
    setOutput(data, true)
    return data
  } catch (error) {
    setOutput(error, false)
    return error
  }
}

async function updateDoc() {
  if (!state.doctype || !state.name) return setOutput({ error: 'doctype and name are required' }, false)
  const parsed = parseJsonField('updateData', 'Update Data')
  if (!parsed.ok) return setOutput({ error: parsed.error }, false)
  const data = parsed.value
  if (!data || Object.keys(data).length === 0) return setOutput({ error: 'Update Data must be a non-empty JSON object' }, false)

  try {
    const result = await put(`/resource/${encodeURIComponent(state.doctype)}/${encodeURIComponent(state.name)}`, data)
    setOutput(result, true)
    return result
  } catch (error) {
    setOutput(error, false)
    return error
  }
}

async function deleteDoc() {
  if (!state.doctype || !state.name) return setOutput({ error: 'doctype and name are required' }, false)

  try {
    const data = await del(`/resource/${encodeURIComponent(state.doctype)}/${encodeURIComponent(state.name)}`)
    setOutput(data, true)
    return data
  } catch (error) {
    setOutput(error, false)
    return error
  }
}

function onFileChange(e) {
  const files = e?.target?.files
  state.fileObj = files && files.length ? files[0] : null
}

async function uploadFileHandler() {
  if (!state.fileObj) {
    const err = { error: 'file is required' }
    setOutput(err, false)
    return err
  }

  try {
    const options = {
      isPrivate: state.isPrivate,
      folder: state.folder,
      doctype: state.attachDoctype,
      docname: state.attachDocname,
      fieldname: state.attachFieldname
    }

    const data = await uploadFile(state.fileObj, options)
    setOutput(data, true)
    return data
  } catch (error) {
    setOutput(error, false)
    return error
  }
}
</script>

<template>
  <div class="p-5 space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="col-span-1">
        <div class="rounded-lg shadow-xl bg-white p-4 space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div class="mb-1 text-sm text-gray-600">Doctype</div>
              <FormControl type="text" v-model="state.doctype" placeholder="ToDo | Course | Homework..." />
            </div>
            <div>
              <div class="mb-1 text-sm text-gray-600">Name</div>
              <FormControl type="text" v-model="state.name" placeholder="Document name (for Read/Update/Delete)" />
            </div>
            <div class="flex items-end gap-2">
              <Button variant="solid" @click="listDocs">List</Button>
              <Button variant="subtle" @click="readDoc">Read</Button>
              <Button variant="subtle" @click="deleteDoc">Delete</Button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div class="mb-1 text-sm text-gray-600">List Params (JSON)</div>
              <div class="flex gap-2 mb-2">
                <Button variant="subtle" @click="formatField('listParams')">Format</Button>
              </div>
              <Textarea rows="6" v-model="state.listParams" />
            </div>
            <div>
              <div class="mb-1 text-sm text-gray-600">Create Data (JSON)</div>
              <div class="flex gap-2 mb-2">
                <Button variant="subtle" @click="formatField('createData')">Format</Button>
              </div>
              <Textarea rows="6" v-model="state.createData" />
            </div>
          </div>

          <div>
            <div class="mb-1 text-sm text-gray-600">Update Data (JSON)</div>
            <div class="flex gap-2 mb-2">
              <Button variant="subtle" @click="formatField('updateData')">Format</Button>
            </div>
            <Textarea rows="4" v-model="state.updateData" />
          </div>

          <div class="flex gap-2">
            <Button variant="solid" @click="createDoc">Create</Button>
            <Button variant="subtle" @click="updateDoc">Update</Button>
          </div>
        </div>
        <div class="rounded-lg shadow-xl bg-white p-4 space-y-4">
          <div class="text-sm text-gray-600">Upload File (multipart/form-data)</div>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div class="mb-1 text-sm text-gray-600">Choose File</div>
              <input type="file" @change="onFileChange" />
            </div>
            <div>
              <div class="mb-1 text-sm text-gray-600">Folder</div>
              <FormControl type="text" v-model="state.folder" placeholder="Home/Homework" />
            </div>
            <div class="flex items-end gap-2">
              <Dropdown
                :options="[{ label: state.isPrivate ? 'Private' : 'Public', onClick: () => state.isPrivate = !state.isPrivate }]">
                <Button variant="subtle">{{ state.isPrivate ? 'Private' : 'Public' }}</Button>
              </Dropdown>
              <Button variant="solid" @click="uploadFileHandler">Upload</Button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <div class="mb-1 text-sm text-gray-600">Attach Doctype (optional)</div>
              <FormControl type="text" v-model="state.attachDoctype" placeholder="e.g. Course" />
            </div>
            <div>
              <div class="mb-1 text-sm text-gray-600">Attach Docname</div>
              <FormControl type="text" v-model="state.attachDocname" placeholder="e.g. COURSE-0001" />
            </div>
            <div>
              <div class="mb-1 text-sm text-gray-600">Attach Fieldname</div>
              <FormControl type="text" v-model="state.attachFieldname" placeholder="e.g. file_homework" />
            </div>
          </div>
        </div>
      </div>
      <div class="col-span-1 rounded-lg shadow-xl bg-white p-4">
        <div class="flex items-center justify-between mb-2">
          <div class="text-sm text-gray-600">Result</div>
          <div class="flex gap-2">
            <Button variant="subtle" @click="formatResult">Format</Button>
            <Button variant="subtle" @click="() => { output = ''; lastRaw = null }">Clear</Button>
          </div>
        </div>
        <pre class="text-xs overflow-auto max-h-[60vh]">{{ output }}</pre>
      </div>
    </div>

  </div>
</template>

<style scoped>
pre {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
