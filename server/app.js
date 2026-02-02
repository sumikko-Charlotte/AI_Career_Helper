/*
  Simple Express server to persist real user data into CSV and expose minimal user APIs.
  - Port: 3000
  - CSV file: public/users.csv (persistent)
  - Endpoints (uniform response): { code: 200/400, msg: '', data: ... }

  Usage:
  1) npm install
  2) node app.js
  3) API examples: GET /api/users, POST /api/register
*/

const express = require('express')
const fs = require('fs')
const path = require('path')
const cors = require('cors')
const csv = require('fast-csv')
const bodyParser = require('body-parser')

const PORT = 3000
const app = express()
app.use(cors())
app.use(bodyParser.json({ limit: '1mb' }))
app.use(bodyParser.urlencoded({ extended: true }))

const CSV_PATH = path.join(__dirname, 'public', 'users.csv')
const CSV_FIELDS = ['username','password','grade','target_role','createTaskNum','uploadedResumeNum','status','register_time','last_login']

// Ensure public folder exists
fs.mkdirSync(path.join(__dirname, 'public'), { recursive: true })

// Helper: read all users from CSV
function readUsers() {
  return new Promise((resolve, reject) => {
    const users = []
    if (!fs.existsSync(CSV_PATH)) return resolve([])
    fs.createReadStream(CSV_PATH)
      .pipe(csv.parse({ headers: true, trim: true }))
      .on('error', err => reject(err))
      .on('data', row => users.push(row))
      .on('end', () => resolve(users))
  })
}

// Helper: write users array back to CSV (overwrites)
function writeUsers(rows) {
  return new Promise((resolve, reject) => {
    const ws = fs.createWriteStream(CSV_PATH)
    csv.write(rows, { headers: true }).pipe(ws).on('finish', resolve).on('error', reject)
  })
}

// Uniform response helpers
function ok(data, msg = '成功') { return { code: 200, msg, data } }
function bad(msg = '失败') { return { code: 400, msg, data: null } }

// Initialize CSV with 10 test users if empty
async function ensureInitialUsers() {
  const users = await readUsers()
  if (users.length === 0) {
    const now = new Date().toISOString().slice(0,19).replace('T',' ')
    const initial = [
      { username: 'alice', password: 'alice123', grade: '大三', target_role: '前端', createTaskNum: '0', uploadedResumeNum: '0', status: 'normal', register_time: now, last_login: '' },
      { username: 'bob', password: 'bob123', grade: '大三', target_role: '后端', createTaskNum: '0', uploadedResumeNum: '0', status: 'normal', register_time: now, last_login: '' },
      { username: 'carol', password: 'carol123', grade: '大四', target_role: '算法', createTaskNum: '0', uploadedResumeNum: '0', status: 'normal', register_time: now, last_login: '' },
      { username: 'dave', password: 'dave123', grade: '大三', target_role: '全栈', createTaskNum: '0', uploadedResumeNum: '0', status: 'normal', register_time: now, last_login: '' },
      { username: 'eve', password: 'eve123', grade: '大二', target_role: '测试', createTaskNum: '0', uploadedResumeNum: '0', status: 'normal', register_time: now, last_login: '' },
      { username: 'frank', password: 'frank123', grade: '大三', target_role: '前端', createTaskNum: '0', uploadedResumeNum: '0', status: 'normal', register_time: now, last_login: '' },
      { username: 'grace', password: 'grace123', grade: '大四', target_role: '后端', createTaskNum: '0', uploadedResumeNum: '0', status: 'normal', register_time: now, last_login: '' },
      { username: 'heidi', password: 'heidi123', grade: '大三', target_role: '算法', createTaskNum: '0', uploadedResumeNum: '0', status: 'normal', register_time: now, last_login: '' },
      { username: 'ivan', password: 'ivan123', grade: '大二', target_role: '全栈', createTaskNum: '0', uploadedResumeNum: '0', status: 'normal', register_time: now, last_login: '' },
      { username: 'judy', password: 'judy123', grade: '大三', target_role: '测试', createTaskNum: '0', uploadedResumeNum: '0', status: 'normal', register_time: now, last_login: '' },
    ]
    await writeUsers(initial)
    console.log('Initialized CSV with 10 test users')
  }
}

// API: register (username, password)
app.post('/api/register', async (req, res) => {
  const { username, password, grade = '', target_role = '' } = req.body || {}
  if (!username || !password) return res.json(bad('用户名和密码为必填'))
  try {
    const users = await readUsers()
    if (users.find(u => u.username === username)) return res.json(bad('用户名已存在'))
    const now = new Date().toISOString().slice(0,19).replace('T',' ')
    const newUser = { username, password, grade, target_role, createTaskNum: '0', uploadedResumeNum: '0', status: 'normal', register_time: now, last_login: '' }
    users.push(newUser)
    await writeUsers(users)
    return res.json(ok(newUser, '注册成功'))
  } catch (e) { console.error(e); return res.json(bad('注册失败')) }
})

// API: login
app.post('/api/login', async (req, res) => {
  const { username, password } = req.body || {}
  if (!username || !password) return res.json(bad('用户名与密码必填'))
  try {
    const users = await readUsers()
    const user = users.find(u => u.username === username && u.password === password)
    if (!user) return res.json(bad('用户名或密码错误'))
    // update last_login
    user.last_login = new Date().toISOString().slice(0,19).replace('T',' ')
    await writeUsers(users)
    return res.json(ok(user, '登录成功'))
  } catch (e) { console.error(e); return res.json(bad('登录失败')) }
})

// API: get users (returns all real users from CSV)
app.get('/api/users', async (req, res) => {
  try {
    const users = await readUsers()
    return res.json(ok(users, '获取用户列表成功'))
  } catch (e) { console.error(e); return res.json(bad('获取用户列表失败')) }
})

// API: update status (username, status)
app.post('/api/user/updateStatus', async (req, res) => {
  const { username, status } = req.body || {}
  if (!username) return res.json(bad('用户名必填'))
  try {
    const users = await readUsers()
    const u = users.find(x => x.username === username)
    if (!u) return res.json(bad('未找到用户'))
    u.status = status || u.status
    await writeUsers(users)
    return res.json(ok(u, '用户状态已更新'))
  } catch (e) { console.error(e); return res.json(bad('更新失败')) }
})

// API: delete user (username)
app.post('/api/user/delete', async (req, res) => {
  const { username } = req.body || {}
  if (!username) return res.json(bad('用户名必填'))
  try {
    let users = await readUsers()
    const exists = users.find(x => x.username === username)
    if (!exists) return res.json(bad('未找到该用户'))
    users = users.filter(x => x.username !== username)
    await writeUsers(users)
    return res.json(ok({}, '删除成功'))
  } catch (e) { console.error(e); return res.json(bad('删除失败')) }
})

// API: add task count (username)
app.post('/api/user/addTask', async (req, res) => {
  const { username } = req.body || {}
  if (!username) return res.json(bad('用户名必填'))
  try {
    const users = await readUsers()
    const u = users.find(x => x.username === username)
    if (!u) return res.json(bad('未找到用户'))
    u.createTaskNum = String((parseInt(u.createTaskNum || '0', 10) || 0) + 1)
    await writeUsers(users)
    return res.json(ok(u, '任务数已更新'))
  } catch (e) { console.error(e); return res.json(bad('更新失败')) }
})

// Start
ensureInitialUsers().then(() => {
  app.listen(PORT, () => console.log(`User server running on port ${PORT}`))
}).catch(e => { console.error('初始化失败', e); process.exit(1) })
