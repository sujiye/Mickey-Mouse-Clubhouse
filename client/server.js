const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 3000;

// 解析 JSON 请求体
app.use(express.json());

// 托管静态文件（让你的 HTML/CSS/JS 能被访问）
app.use(express.static(__dirname));

// 数据文件路径
const USER_FILE = path.join(__dirname, 'users.json');
const FEED_FILE = path.join(__dirname, 'feedback.json');

// 自动创建数据文件
if (!fs.existsSync(USER_FILE)) fs.writeFileSync(USER_FILE, '[]');
if (!fs.existsSync(FEED_FILE)) fs.writeFileSync(FEED_FILE, '[]');

// 根路径重定向到你的注册页面（关键！支持中文文件名）
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '注册.html'));
});

// 注册接口
app.post('/register', (req, res) => {
    const { username, password, email } = req.body; // 添加 email
    const users = JSON.parse(fs.readFileSync(USER_FILE, 'utf-8'));
    
    if (users.find(u => u.username === username))
        return res.status(409).json({ msg: '用户已存在' });
    
    users.push({ username, password, email }); // 添加 email 到用户对象
    fs.writeFileSync(USER_FILE, JSON.stringify(users, null, 2));
    res.json({ msg: '注册成功' });
});

// 登录接口
app.post('/login', (req, res) => {
    const { username, password } = req.body;
    const users = JSON.parse(fs.readFileSync(USER_FILE, 'utf-8'));
    
    // 检查用户名或邮箱是否存在
    const user = users.find(u => u.username === username || u.email === username);
    
    if (!user) {
        return res.status(401).json({ msg: '用户名或邮箱不存在' });
    }

    // 检查密码是否正确
    if (user.password !== password) {
        return res.status(401).json({ msg: '密码错误' });
    }

    // 登录成功
    res.json({ msg: '登录成功', user: user });
});

// 启动服务器（监听所有网卡，支持局域网）
app.listen(PORT, '0.0.0.0', () => {
    console.log(`\n========================================`);
    console.log(`✅ 服务器启动成功！`);
    console.log(`📍 本机访问:   http://localhost:${PORT}`);
    console.log(`🌐 局域网访问: http://${getLocalIp()}:${PORT}`);
    console.log(`========================================\n`);
});

// 获取本机 IP 函数
function getLocalIp() {
    const interfaces = require('os').networkInterfaces();
    for (const name of Object.keys(interfaces)) {
        for (const interface of interfaces[name]) {
            if (interface.family === 'IPv4' && !interface.internal && interface.address.startsWith('192.168.')) {
                return interface.address;
            }
        }
    }
    return 'localhost';
}